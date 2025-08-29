#!/usr/bin/env python3
"""
Command Processor Module
Handles command matching and processing using sentence embeddings
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class CommandProcessor:
    def __init__(self):
        # Initialize sentence transformer model
        print("Loading sentence transformer model...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Define available commands
        self.commands = [
            "turn on all lights", "turn on bedroom lights", "turn off bedroom lights",
            "turn off living room lamp", "turn on living room lamp", "turn off all lights",
            "get weather", "get time", "set timer", "play music or song", "call for help", 
            "Search for bluetooth speaker"
        ]

        # Define available songs
        self.songs = [
            "Manathe Chandanakkeeru", "Entammede Jimikki Kammal", "Aaro Viral Meeti",
            "Kizhakku Pookkum", "Mazhaye Thoomazhaye", "Oru Madhurakinavin",
            "Ponveene", "Thumbi Vaa", "Melle Melle", "Nee Himamazhayayi"
        ]

        # Pre-compute embeddings
        print("Computing command embeddings...")
        self.command_embeddings = self.sentence_model.encode(self.commands)
        self.song_embeddings = self.sentence_model.encode(self.songs)
        
    def process_command(self, text, command_threshold=80, song_threshold=50):
        """Process user input and find best matching command and song"""
        if not text.strip():
            return None, 0, None, 0

        user_embedding = self.sentence_model.encode(text)

        # Check commands
        similarities = cosine_similarity([user_embedding], self.command_embeddings)
        best_match_index = similarities.argmax()
        best_command = self.commands[best_match_index]
        command_confidence = similarities[0, best_match_index] * 100

        song_match = None
        song_confidence = 0

        # If it's a music command, also check songs
        if command_confidence > song_threshold and best_command == "play music or song":
            song_similarities = cosine_similarity([user_embedding], self.song_embeddings)
            best_song_index = song_similarities.argmax()
            song_match = self.songs[best_song_index]
            song_confidence = song_similarities[0, best_song_index] * 100

        # If confidence is too low, defer to LLM
        if command_confidence < command_threshold:
            best_command = "Lets ask LLM"

        return best_command, command_confidence, song_match, song_confidence
