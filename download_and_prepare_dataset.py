import os
import json
import urllib.request
import zipfile
import pickle
import random
from collections import defaultdict

def download_cornell_dataset():
    """Download Cornell Movie Dialogs Corpus"""
    print("[INFO] Downloading Cornell Movie Dialogs Corpus...")
    
    url = "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
    dataset_dir = "cornell_dataset"
    
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    
    zip_path = os.path.join(dataset_dir, "cornell_dataset.zip")
    
    if not os.path.exists(zip_path):
        try:
            urllib.request.urlretrieve(url, zip_path)
            print("[INFO] Dataset downloaded successfully!")
        except Exception as e:
            print(f"[WARNING] Could not download Cornell dataset: {e}")
            print("[INFO] Using existing conversational patterns instead...")
            return False
    
    # Extract zip file
    if not os.path.exists(os.path.join(dataset_dir, "cornell movie-dialogs corpus")):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(dataset_dir)
            print("[INFO] Dataset extracted successfully!")
        except Exception as e:
            print(f"[WARNING] Could not extract dataset: {e}")
            return False
    
    return True

def process_cornell_dataset():
    """Process Cornell dataset into conversational intents"""
    print("[INFO] Processing Cornell Movie Dialogs Corpus...")
    
    corpus_dir = "cornell_dataset/cornell movie-dialogs corpus"
    conversations_file = os.path.join(corpus_dir, "movie_conversations.txt")
    lines_file = os.path.join(corpus_dir, "movie_lines.txt")
    
    if not os.path.exists(conversations_file) or not os.path.exists(lines_file):
        print("[WARNING] Cornell files not found, using fallback dataset")
        return None
    
    # Load lines
    lines = {}
    try:
        with open(lines_file, 'r', encoding='iso-8859-1') as f:
            for line in f:
                parts = line.split(" +++$+++ ")
                if len(parts) >= 5:
                    line_id = parts[0].strip()
                    text = parts[4].strip()
                    lines[line_id] = text
    except Exception as e:
        print(f"[WARNING] Error reading lines file: {e}")
        return None
    
    # Load conversations and create conversation pairs
    conversation_pairs = []
    try:
        with open(conversations_file, 'r', encoding='iso-8859-1') as f:
            for line in f:
                parts = line.split(" +++$+++ ")
                if len(parts) >= 4:
                    line_ids = parts[3].strip(" []\n").split(", ")
                    for i in range(len(line_ids) - 1):
                        line_id1 = line_ids[i].strip().strip("'\"")
                        line_id2 = line_ids[i + 1].strip().strip("'\"")
                        
                        if line_id1 in lines and line_id2 in lines:
                            text1 = lines[line_id1].lower()
                            text2 = lines[line_id2].lower()
                            
                            # Filter short texts and quality
                            if len(text1.split()) >= 2 and len(text2.split()) >= 2:
                                if len(text1) < 200 and len(text2) < 200:
                                    conversation_pairs.append((text1, text2))
    except Exception as e:
        print(f"[WARNING] Error reading conversations file: {e}")
        return None
    
    print(f"[INFO] Found {len(conversation_pairs)} conversation pairs")
    return conversation_pairs

def create_dataset_from_conversations(conversation_pairs):
    """Convert conversation pairs into intent-based JSON format"""
    print("[INFO] Creating intent-based dataset...")
    
    intents = defaultdict(lambda: {"tag": "", "patterns": set(), "responses": set(), "context_set": ""})
    
    # Example-based categorization
    greeting_words = ["hi", "hello", "hey", "greetings", "welcome", "howdy"]
    farewell_words = ["bye", "goodbye", "see you", "farewell", "good bye", "take care"]
    question_words = ["what", "how", "where", "when", "why", "who", "which"]
    agreement_words = ["yes", "yeah", "sure", "ok", "okay", "alright", "definitely"]
    
    # Distribute conversations into intent categories
    intents["greeting"]["tag"] = "greeting"
    intents["goodbye"]["tag"] = "goodbye"
    intents["question"]["tag"] = "question"
    intents["statement"]["tag"] = "statement"
    intents["agreement"]["tag"] = "agreement"
    intents["disagreement"]["tag"] = "disagreement"
    
    for line1, line2 in conversation_pairs:
        # Categorize each line
        line1_lower = line1.lower()
        line2_lower = line2.lower()
        
        # Greeting detection
        if any(word in line1_lower for word in greeting_words):
            intents["greeting"]["patterns"].add(line1)
            intents["greeting"]["responses"].add(line2)
        
        # Farewell detection
        if any(word in line1_lower for word in farewell_words):
            intents["goodbye"]["patterns"].add(line1)
            intents["goodbye"]["responses"].add(line2)
        
        # Question detection
        if any(word in line1_lower.split() for word in question_words):
            intents["question"]["patterns"].add(line1)
            intents["question"]["responses"].add(line2)
        
        # Agreement detection
        if any(agreement_words[0] in line1_lower for word in agreement_words):
            intents["agreement"]["patterns"].add(line1)
            intents["agreement"]["responses"].add(line2)
        
        # General statements
        else:
            intents["statement"]["patterns"].add(line1)
            intents["statement"]["responses"].add(line2)
    
    # Convert sets to lists and filter
    final_intents = []
    for tag, intent_data in intents.items():
        patterns = list(intent_data["patterns"])[:50]  # Limit patterns
        responses = list(intent_data["responses"])[:50]  # Limit responses
        
        if patterns and responses:
            final_intents.append({
                "tag": intent_data["tag"],
                "patterns": patterns,
                "responses": responses,
                "context_set": ""
            })
    
    return final_intents

def get_fallback_dataset():
    """Return fallback conversational dataset"""
    print("[INFO] Using comprehensive fallback conversational dataset...")
    
    return {
        "intents": [
            {
                "tag": "greeting",
                "patterns": ["Hi", "Hello", "How are you", "Good morning", "Good afternoon", "Good evening", "Hey", "Greetings", "What's up", "Howdy", "G'day", "Welcome", "Good day", "Is anyone there?", "Hiya", "Hi there", "Hello there", "Good to see you", "Nice to meet you"],
                "responses": ["Hello! How can I help you today?", "Hi there! What can I do for you?", "Greetings! How may I assist you?", "Hey! How's it going?", "Welcome! What brings you here?", "Hi! Nice to see you!"],
                "context_set": ""
            },
            {
                "tag": "goodbye",
                "patterns": ["bye", "goodbye", "bye bye", "see you", "see you later", "see ya", "take care", "farewell", "catch you", "talk to you later", "ttyl", "gotta go", "have a good day", "have a nice day", "take it easy", "peace", "hasta la vista", "adios", "cheerio", "see you soon"],
                "responses": ["Goodbye! Have a great day!", "Bye! Talk to you later!", "See you soon!", "Take care!", "Farewell! Have a wonderful day!"],
                "context_set": ""
            },
            {
                "tag": "thank_you",
                "patterns": ["thanks", "thank you", "appreciate it", "appreciate your help", "much appreciated", "thanks a lot", "thanks so much", "thank you so much", "you're awesome", "thank you very much", "many thanks", "thanks buddy", "thanks mate", "I appreciate that"],
                "responses": ["You're welcome!", "Happy to help!", "Anytime!", "Glad I could assist!"],
                "context_set": ""
            },
            {
                "tag": "sorry",
                "patterns": ["sorry", "my apologies", "my bad", "excuse me", "pardon me", "sorry about that", "my mistake", "I apologize", "forgive me", "my sincere apologies", "terribly sorry"],
                "responses": ["No problem at all!", "Don't worry about it!", "It's okay!", "No worries!", "Don't mention it!"],
                "context_set": ""
            },
            {
                "tag": "identity",
                "patterns": ["who are you?", "what are you?", "tell me about yourself", "who do you work for?", "what's your name?", "introduce yourself", "who am I talking to?", "are you a robot?", "are you human?", "what's your purpose?", "tell me about you"],
                "responses": ["I am an AI Chatbot designed to assist you with common questions and conversations.", "I'm a virtual assistant here to help answer your questions!", "I'm an intelligent chatbot created to provide support and information."],
                "context_set": ""
            },
            {
                "tag": "help",
                "patterns": ["help", "can you help me?", "I need help", "I need assistance", "assist me", "support me", "can you assist?", "help me please", "I'm stuck", "what can you do?", "what are your capabilities?"],
                "responses": ["Of course! I'm here to help. What do you need assistance with?", "I'd be happy to help! What's the issue?", "Sure, I can assist you. What do you need?", "How can I help you today?"],
                "context_set": ""
            },
            {
                "tag": "how_are_you",
                "patterns": ["how are you?", "how are you doing?", "how's it going?", "how's everything?", "how are things?", "are you okay?", "how do you feel?", "what's up?", "how's your day?"],
                "responses": ["I'm doing well, thank you for asking!", "I'm great! Thanks for asking. How about you?", "All good here! How are you doing?", "I'm functioning perfectly! How can I help?"],
                "context_set": ""
            },
            {
                "tag": "name_ask",
                "patterns": ["what's your name?", "who are you called?", "what do I call you?", "your name?", "do you have a name?", "tell me your name"],
                "responses": ["I'm a helpful AI Assistant!", "You can call me ChatBot!", "I'm your virtual assistant!"],
                "context_set": ""
            },
            {
                "tag": "weather",
                "patterns": ["what's the weather like?", "how's the weather?", "is it raining?", "is it sunny?", "what's the temperature?", "weather forecast", "weather update"],
                "responses": ["I don't have real-time weather data, but you can check a weather service!", "For weather information, I recommend checking a weather website or app."],
                "context_set": ""
            },
            {
                "tag": "time",
                "patterns": ["what time is it?", "what's the time?", "what time now?", "current time", "tell me the time"],
                "responses": ["I don't have access to the current time, but you can check your device!", "You can see the time on your device or a clock."],
                "context_set": ""
            },
            {
                "tag": "questions",
                "patterns": ["how do I?", "can you teach me?", "explain this", "what does this mean?", "I don't understand", "can you explain?", "I'm confused"],
                "responses": ["I'd be happy to explain! Could you be more specific?", "Let me help clarify that for you.", "Sure! What exactly would you like to know more about?"],
                "context_set": ""
            },
            {
                "tag": "positive",
                "patterns": ["nice", "good", "great", "excellent", "awesome", "love it", "wonderful", "fantastic", "amazing", "perfect", "brilliant", "superb"],
                "responses": ["That's wonderful to hear!", "I'm glad you're happy!", "That makes me happy too!", "Fantastic!"],
                "context_set": ""
            },
            {
                "tag": "negative",
                "patterns": ["bad", "horrible", "terrible", "awful", "hate it", "don't like", "dislike", "not good", "worse", "annoying", "frustrating"],
                "responses": ["I'm sorry to hear that!", "I understand your frustration.", "Let me know how I can help improve things!", "I'm here to assist!"],
                "context_set": ""
            },
            {
                "tag": "affirmation",
                "patterns": ["yes", "yeah", "sure", "okay", "ok", "alright", "absolutely", "definitely", "of course", "certainly", "yep", "yup"],
                "responses": ["Great! How can I help?", "Perfect! What's next?", "Excellent! Let's proceed."],
                "context_set": ""
            },
            {
                "tag": "negation",
                "patterns": ["no", "nope", "not really", "don't think so", "nah", "negative", "definitely not", "no way"],
                "responses": ["No problem! Is there anything else I can help with?", "That's okay! What else can I assist you with?"],
                "context_set": ""
            }
        ]
    }

def main():
    print("[INFO] Starting dataset preparation...")
    
    # Try to download Cornell dataset
    if download_cornell_dataset():
        conversation_pairs = process_cornell_dataset()
        if conversation_pairs:
            intents = create_dataset_from_conversations(conversation_pairs)
            # Merge with fallback dataset
            fallback = get_fallback_dataset()
            combined_intents = fallback["intents"] + intents
            dataset = {"intents": combined_intents}
        else:
            dataset = get_fallback_dataset()
    else:
        dataset = get_fallback_dataset()
    
    # Save dataset
    dataset_path = 'dataset/dataset.json'
    os.makedirs('dataset', exist_ok=True)
    
    with open(dataset_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"[INFO] Dataset saved to {dataset_path}")
    print(f"[INFO] Total intents: {len(dataset['intents'])}")
    print(f"[INFO] Dataset preparation complete!")

if __name__ == "__main__":
    main()
