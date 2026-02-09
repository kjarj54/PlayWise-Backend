"""
Servicio de Recomendaciones con IA (Groq)
Genera recomendaciones personalizadas basadas en el historial del usuario
"""

from sqlmodel import Session, select
from typing import List, Dict, Optional
import json
import httpx
from app.models.user import User
from app.models.calification import CalificationGame
from app.models.wishlist import WishList
from app.models.game import Game
from app.core.config import settings


class RecommendationService:
    """Servicio para generar recomendaciones de juegos usando IA (Groq)"""
    
    def __init__(self):
        """Inicializa el cliente de Groq API"""
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"  # Modelo gratis y potente
        
        print(f"✅ Groq API inicializada con modelo: {self.model}")
    
    @staticmethod
    def get_user_history(session: Session, user_id: int) -> Dict:
        """Obtiene el historial completo del usuario"""
        
        # Calificaciones altas (>= 7)
        high_rated_query = (
            select(CalificationGame, Game)
            .join(Game, CalificationGame.game_id == Game.id)
            .where(CalificationGame.user_id == user_id)
            .where(CalificationGame.score >= 7)
        )
        high_rated = session.exec(high_rated_query).all()
        
        # Wishlist
        wishlist_query = (
            select(WishList, Game)
            .join(Game, WishList.game_id == Game.id)
            .where(WishList.user_id == user_id)
        )
        wishlist = session.exec(wishlist_query).all()
        
        # Extraer información relevante (filtrar juegos de prueba)
        test_keywords = ['test', 'teste', 'prueba', 'demo', 'local']
        
        liked_games = [
            {
                "name": game.name,
                "genre": game.genre,
                "rating": cal.score
            }
            for cal, game in high_rated
            if not any(keyword in game.name.lower() for keyword in test_keywords)
        ]
        
        wishlist_games = [
            {
                "name": game.name,
                "genre": game.genre
            }
            for wl, game in wishlist
            if not any(keyword in game.name.lower() for keyword in test_keywords)
        ]
        
        # Lista de juegos que YA tiene el usuario (para NO recomendarlos)
        existing_games = set()
        for cal, game in high_rated:
            if not any(keyword in game.name.lower() for keyword in test_keywords):
                existing_games.add(game.name)
        for wl, game in wishlist:
            if not any(keyword in game.name.lower() for keyword in test_keywords):
                existing_games.add(game.name)
        
        # Extraer géneros favoritos
        all_genres = []
        for cal, game in high_rated:
            if game.genre:
                all_genres.extend([g.strip() for g in game.genre.split(',')])
        
        for wl, game in wishlist:
            if game.genre:
                all_genres.extend([g.strip() for g in game.genre.split(',')])
        
        # Contar frecuencia de géneros
        genre_count = {}
        for genre in all_genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1
        
        # Top 5 géneros
        favorite_genres = sorted(
            genre_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "liked_games": liked_games,
            "wishlist_games": wishlist_games,
            "favorite_genres": [genre for genre, _ in favorite_genres],
            "existing_games": list(existing_games)
        }
    
    def generate_recommendations(
        self, 
        session: Session, 
        user_id: int,
        count: int = 5
    ) -> List[Dict]:
        """Genera recomendaciones usando Gemini AI"""
        
        print(f"\n{'='*60}")
        print(f"🎯 GENERANDO RECOMENDACIONES PARA USER_ID: {user_id}")
        print(f"{'='*60}")
        
        # Obtener historial del usuario
        history = self.get_user_history(session, user_id)
        
        print(f"\n📊 HISTORIAL DEL USUARIO:")
        print(f"   💚 Juegos que le gustaron: {len(history['liked_games'])}")
        for i, game in enumerate(history['liked_games'][:5], 1):
            print(f"      {i}. {game['name']} ({game['rating']}/10)")
        print(f"   ⭐ Wishlist: {len(history['wishlist_games'])}")
        for i, game in enumerate(history['wishlist_games'][:5], 1):
            print(f"      {i}. {game['name']}")
        print(f"   🎮 Géneros favoritos: {', '.join(history['favorite_genres'])}")
        print(f"   🚫 Juegos que YA tiene: {len(history['existing_games'])}")
        
        # Si no hay datos suficientes, recomendar populares
        if not history["liked_games"] and not history["wishlist_games"]:
            print(f"\n⚠️ Sin datos suficientes, devolviendo juegos populares...")
            return self.get_popular_games(session, count)
        
        # Construir prompt para Gemini
        prompt = self._build_prompt(history, count)
        
        try:
            # Llamar a Groq API para obtener NOMBRES de juegos
            print(f"\n{'='*60}")
            print(f"🤖 LLAMANDO A GROQ AI (Llama 3)...")
            print(f"{'='*60}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 1.2,
                "max_tokens": 2000,
                "top_p": 0.95
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
            
            print(f"\n📝 RESPUESTA DE GROQ:")
            print(ai_response)
            print(f"{'='*60}\n")
            
            # Parsear respuesta (solo nombres de juegos)
            recommended_names = self._parse_gemini_response(ai_response)
            
            print(f"✅ Juegos parseados de Groq: {len(recommended_names)}")
            for i, game in enumerate(recommended_names, 1):
                print(f"  {i}. {game.get('name')} - {game.get('genre')}")
            
            # Buscar cada juego en RAWG API
            recommendations = []
            print(f"\n🔍 BUSCANDO EN RAWG API...")
            print(f"{'='*60}")
            
            for game_rec in recommended_names[:count]:
                print(f"\n🎮 Buscando: '{game_rec['name']}'...")
                rawg_data = self._search_game_in_rawg(game_rec["name"])
                
                if rawg_data:
                    print(f"   ✅ Encontrado: {rawg_data.get('name')}")
                    recommendations.append({
                        "name": rawg_data.get("name", game_rec["name"]),
                        "genre": ", ".join([g["name"] for g in rawg_data.get("genres", [])]) or game_rec.get("genre", "Varios"),
                        "reason": game_rec.get("reason", "Recomendado para ti"),
                        "similarity_score": game_rec.get("similarity_score", 80),
                        "api_id": str(rawg_data.get("id", "")),
                        "cover_image": rawg_data.get("background_image"),
                        "rating": rawg_data.get("rating"),
                        "released": rawg_data.get("released"),
                    })
                else:
                    print(f"   ❌ NO encontrado en RAWG")
                    # Si no se encuentra en RAWG, usar datos de Gemini
                    recommendations.append(game_rec)
            
            print(f"\n{'='*60}")
            print(f"✨ TOTAL RECOMENDACIONES: {len(recommendations)}")
            print(f"{'='*60}\n")
            
            return recommendations[:count]
            
        except Exception as e:
            print(f"❌ Error con Groq API: {e}")
            import traceback
            traceback.print_exc()
            # Fallback a recomendaciones por géneros
            return self.get_recommendations_by_genre(
                session, 
                history["favorite_genres"],
                count,
                exclude_games=history.get("existing_games", [])
            )
    
    def _build_prompt(self, history: Dict, count: int) -> str:
        """Construye el prompt para Groq"""
        
        import random
        from datetime import datetime
        
        # Agregar variabilidad temporal
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        random_seed = random.randint(1, 10000)
        
        print(f"\n📝 CONSTRUYENDO PROMPT...")
        print(f"   🎲 Random Seed: {random_seed}")
        print(f"   ⏰ Timestamp: {timestamp}")
        print(f"   🎮 Juegos que ya tiene: {len(history.get('existing_games', []))}")
        if history.get('existing_games'):
            print(f"   📋 Primeros 5: {history['existing_games'][:5]}")
        
        prompt = f"""Eres un experto en videojuegos. Basándote en el historial del usuario, recomienda {count} juegos DIFERENTES.

IMPORTANTE: Esta es la solicitud #{random_seed} del {timestamp}. Debes dar recomendaciones VARIADAS y DIFERENTES a solicitudes anteriores.

HISTORIAL DEL USUARIO:

Juegos que le gustaron (calificación alta):
"""
        
        for game in history["liked_games"][:10]:
            prompt += f"- {game['name']} ({game['genre']}) - Rating: {game['rating']}/10\n"
        
        if history["wishlist_games"]:
            prompt += "\nJuegos en su wishlist:\n"
            for game in history["wishlist_games"][:10]:
                prompt += f"- {game['name']} ({game['genre']})\n"
        
        prompt += f"\nGéneros favoritos: {', '.join(history['favorite_genres'])}\n"
        
        # Lista de juegos que NO debe recomendar
        if history.get("existing_games"):
            prompt += "\n⚠️ JUEGOS QUE EL USUARIO YA TIENE (NO RECOMENDARLOS):\n"
            for game_name in history["existing_games"][:15]:  # Limitar a 15 para no saturar el prompt
                prompt += f"- {game_name}\n"
        
        prompt += f"""

INSTRUCCIONES CRÍTICAS:
1. Recomienda {count} juegos REALES de la industria (AAA, indies populares, etc.)
2. NUNCA repitas los juegos de la lista de arriba (que ya tiene)
3. SÉ CREATIVO: Da títulos DIFERENTES cada vez, explora distintos subgéneros
4. Mezcla juegos modernos (2020-2026) con clásicos populares
5. Incluye tanto juegos AAA como indies reconocidos
6. Varía entre juegos famosos y joyas ocultas del mismo género
7. PROHIBIDO repetir recomendaciones de solicitudes anteriores

EJEMPLOS de variedad (NO uses estos, solo de referencia):
- Si le gusta RPG: The Witcher 3, Elden Ring, Baldur's Gate 3, Disco Elysium, Divinity 2
- Si le gusta Shooter: Call of Duty, Valorant, Apex Legends, Halo Infinite, Destiny 2
- Si le gusta Aventura: The Last of Us, God of War, Uncharted, Tomb Raider, Horizon

FORMATO DE RESPUESTA (JSON estricto):
{{
  "recommendations": [
    {{
      "name": "Nombre del Juego",
      "genre": "Género principal",
      "reason": "Breve explicación de por qué lo recomiendas (máximo 50 palabras)",
      "similarity_score": 85
    }}
  ]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parsea la respuesta de Gemini"""
        try:
            # Limpiar la respuesta (remover markdown si existe)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            clean_text = clean_text.strip()
            
            # Parsear JSON
            data = json.loads(clean_text)
            return data.get("recommendations", [])
            
        except json.JSONDecodeError as e:
            print(f"Error parseando respuesta de Gemini: {e}")
            print(f"Respuesta recibida: {response_text}")
            return []
    
    def _search_game_in_rawg(self, game_name: str) -> Optional[Dict]:
        """Busca un juego en RAWG API por nombre"""
        if not settings.RAWG_API_KEY:
            print("⚠️ RAWG_API_KEY no configurada")
            return None
        
        try:
            url = f"https://api.rawg.io/api/games"
            params = {
                "key": settings.RAWG_API_KEY,
                "search": game_name,
                "page_size": 1,
                "search_precise": True
            }
            
            print(f"      🌐 URL: {url}")
            print(f"      🔑 API Key: {settings.RAWG_API_KEY[:20]}...")
            print(f"      🔎 Buscando: '{game_name}'")
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                
                print(f"      📡 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    print(f"      📊 Resultados: {len(results)}")
                    
                    if results:
                        game = results[0]
                        print(f"      ✅ Encontrado: '{game.get('name')}' (ID: {game.get('id')})")
                        print(f"         Imagen: {game.get('background_image', 'N/A')[:50]}...")
                        return game
                    else:
                        print(f"      ⚠️ Sin resultados para '{game_name}'")
                else:
                    print(f"      ❌ Error HTTP: {response.status_code}")
                    print(f"      Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"      🚨 Error buscando en RAWG: {e}")
        
        return None
    
    @staticmethod
    def get_popular_games(session: Session, count: int = 5) -> List[Dict]:
        """Fallback: devuelve juegos populares si no hay historial"""
        
        test_keywords = ['test', 'teste', 'prueba', 'demo', 'local']
        
        query = (
            select(Game)
            .where(Game.api_rating.isnot(None))
            .order_by(Game.api_rating.desc())
            .limit(count * 2)  # Obtener más para poder filtrar
        )
        
        games = session.exec(query).all()
        
        # Filtrar juegos de prueba
        filtered_games = [
            game for game in games
            if not any(keyword in game.name.lower() for keyword in test_keywords)
        ]
        
        return [
            {
                "name": game.name,
                "genre": game.genre or "Varios",
                "reason": "Juego altamente calificado por la comunidad",
                "similarity_score": 70,
                "id": game.id,
                "api_id": game.api_id,
                "cover_image": game.cover_image
            }
            for game in filtered_games[:count]
        ]
    
    @staticmethod
    def get_recommendations_by_genre(
        session: Session, 
        favorite_genres: List[str], 
        count: int = 5,
        exclude_games: List[str] = []
    ) -> List[Dict]:
        """Fallback: recomendaciones basadas en géneros favoritos"""
        
        if not favorite_genres:
            return RecommendationService.get_popular_games(session, count)
        
        # Buscar juegos de géneros favoritos
        recommendations = []
        test_keywords = ['test', 'teste', 'prueba', 'demo', 'local']
        
        for genre in favorite_genres:
            query = (
                select(Game)
                .where(Game.genre.contains(genre))
                .order_by(Game.api_rating.desc())
                .limit(count * 3)  # Obtener más para poder filtrar
            )
            
            games = session.exec(query).all()
            
            for game in games:
                if len(recommendations) >= count:
                    break
                
                # Saltar si es juego de prueba
                if any(keyword in game.name.lower() for keyword in test_keywords):
                    continue
                
                # Saltar si el usuario ya lo tiene
                if game.name in exclude_games:
                    continue
                    
                recommendations.append({
                    "name": game.name,
                    "genre": game.genre or genre,
                    "reason": f"Te gusta el género {genre}",
                    "similarity_score": 75,
                    "id": game.id,
                    "api_id": game.api_id,
                    "cover_image": game.cover_image
                })
            
            if len(recommendations) >= count:
                break
        
        return recommendations[:count]
