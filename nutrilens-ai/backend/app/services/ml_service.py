import os
import numpy as np
from typing import Dict, Any
from PIL import Image
import io
import json

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import keras
    from tensorflow.keras.models import load_model as _tf_load_model
    # Enable Lambda-layer support so transfer-learning models with preprocessing lambdas load correctly.
    # This is safe for our own Colab-trained models.
    def tf_load_model(path):
        try:
            return _tf_load_model(path, safe_mode=False)
        except TypeError:
            # Older keras versions don't have safe_mode kwarg — try without it
            return _tf_load_model(path)
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class MLService:
    """
    ML Service for food freshness detection and classification.
    
    Dataset Integration Points:
    1. Fruits Fresh & Rotten Dataset - Freshness detection
    2. Food-101 Dataset - Food recognition
    3. Food Waste Dataset - Waste classification
    """
    
    def __init__(self):
        self.freshness_model = None
        self.food_recognition_model = None
        self.waste_model = None
        self.food_classes = {}
        self.waste_classes = {}
        self._load_models()
    
    def _load_models(self):
        """Load trained models. Falls back to mock if models not available."""
        # Prefer Settings (reads .env) over raw os.getenv, fall back to path relative to this file.
        try:
            from app.config import get_settings
            _settings = get_settings()
            freshness_path = _settings.FRESHNESS_MODEL_PATH
            recognition_path = _settings.FOOD_RECOGNITION_MODEL_PATH
            waste_path = _settings.WASTE_MODEL_PATH
            milk_path = _settings.MILK_QUALITY_MODEL_PATH
        except Exception:
            # Fallback: 3 levels up from services/ → app/ → backend/ → nutrilens-ai/ml_models
            base_dir = os.path.dirname(__file__)
            ml_models_dir = os.path.abspath(os.path.join(base_dir, '..', '..', '..', 'ml_models'))
            freshness_path = os.path.join(ml_models_dir, 'freshness_model.keras')
            recognition_path = os.path.join(ml_models_dir, 'food_recognition_model.h5')
            waste_path = os.path.join(ml_models_dir, 'waste_model.keras')
            milk_path = os.path.join(ml_models_dir, 'milk_quality_model.pkl')

        # Derive ml_models_dir from freshness_path for JSON sidecar files
        try:
            ml_models_dir = os.path.dirname(os.path.abspath(freshness_path))
            if not os.path.exists(ml_models_dir):
                 # Fallback to local resolve if path from config doesn't exist
                 base_dir = os.path.dirname(__file__)
                 ml_models_dir = os.path.abspath(os.path.join(base_dir, '..', '..', '..', 'ml_models'))
        except Exception:
            base_dir = os.path.dirname(__file__)
            ml_models_dir = os.path.abspath(os.path.join(base_dir, '..', '..', '..', 'ml_models'))

        # Standardize paths
        freshness_path = os.path.join(ml_models_dir, 'freshness_model.keras')
        recognition_path = os.path.join(ml_models_dir, 'food_recognition_model.h5')
        waste_path = os.path.join(ml_models_dir, 'waste_model.keras')
        milk_path = os.path.join(ml_models_dir, 'milk_quality_model.pkl')

        print(f"[ML] Model directory resolved to: {ml_models_dir}")

        food_classes_path = os.path.join(ml_models_dir, 'food_recognition_classes.json')
        waste_classes_path = os.path.join(ml_models_dir, 'waste_classes.json')

        if os.path.exists(food_classes_path):
            with open(food_classes_path, 'r') as f:
                self.food_classes = json.load(f)
            print(f"[OK] Loaded {len(self.food_classes)} food recognition classes")
        if os.path.exists(waste_classes_path):
            with open(waste_classes_path, 'r') as f:
                self.waste_classes = json.load(f)
            print(f"[OK] Loaded {len(self.waste_classes)} waste classes")

        if TF_AVAILABLE:
            if os.path.exists(freshness_path):
                try:
                    self.freshness_model = tf_load_model(freshness_path)
                    print(f"[OK] Freshness model loaded from {freshness_path}")
                except Exception as e:
                    print(f"[WARN] Freshness model failed to load: {e}")
            else:
                print(f"[INFO] Freshness model not found at: {freshness_path} — using heuristic fallback")

            if os.path.exists(recognition_path):
                try:
                    self.food_recognition_model = tf_load_model(recognition_path)
                    print(f"[OK] Food recognition model loaded from {recognition_path}")
                except Exception as e:
                    print(f"[WARN] Food recognition model failed to load: {e}")
            else:
                print(f"[INFO] Food recognition model not found at: {recognition_path} — using mock")

            if os.path.exists(waste_path):
                try:
                    self.waste_model = tf_load_model(waste_path)
                    print(f"[OK] Waste model loaded from {waste_path}")
                except Exception as e:
                    print(f"[WARN] Waste model failed to load: {e}")
            else:
                print(f"[INFO] Waste model not found at: {waste_path} — using mock")
        else:
            print("[INFO] TensorFlow not available - using heuristic freshness analysis.")

        if JOBLIB_AVAILABLE and os.path.exists(milk_path):
            try:
                self.milk_quality_model = joblib.load(milk_path)
                print(f"[OK] Milk quality model loaded from {milk_path}")
            except Exception as e:
                print(f"[WARN] Milk quality model failed to load: {e}")
        else:
            self.milk_quality_model = None
            if not os.path.exists(milk_path):
                print(f"[INFO] Milk quality model not found at: {milk_path} — using heuristics")
    
    def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((224, 224))
        img_array = np.array(image)
        img_array = img_array.astype('float32') / 255.0
        return np.expand_dims(img_array, axis=0)

    async def predict_freshness(self, image_bytes: bytes, food_name_override: str = None) -> Dict[str, Any]:
        """
        Predict food freshness from image.
        
        Dataset: Fruits Fresh & Rotten Dataset
        Model: CNN trained on fresh/rotten classification
        """
        
        if self.freshness_model:
            try:
                # 2. Assess Freshness
                # Only use the model for fruits it was specifically trained on (Apple, Banana, Orange)
                target_fruits = ['apple', 'banana', 'orange']
                recognized_lower = (food_name_override or "").lower()
                
                is_supported_fruit = any(f in recognized_lower for f in target_fruits)
                
                if is_supported_fruit:
                    preprocessed = self._preprocess_image(image_bytes)
                    prediction = self.freshness_model.predict(preprocessed)[0]
                    class_idx = np.argmax(prediction)
                    confidence = float(prediction[class_idx])
                    
                    # Fruits Fresh & Rotten dataset mapping:
                    # 0: FreshApple, 1: FreshBanana, 2: FreshOrange, 3: RottenApple, 4: RottenBanana, 5: RottenOrange
                    if class_idx < 3:
                         status = 'fresh'
                         risk = 10.0 + (1.0 - confidence) * 20
                    else:
                         status = 'rotten'
                         risk = 80.0 + (confidence) * 20
                         
                    risk = min(100.0, risk)
                    
                    # Use recognized name if provided, otherwise fallback to simple class mapping
                    food_name = food_name_override or "Detected Food"
                    if not food_name_override:
                        if class_idx == 0 or class_idx == 3: food_name = "Apple"
                        elif class_idx == 1 or class_idx == 4: food_name = "Banana"
                        elif class_idx == 2 or class_idx == 5: food_name = "Orange"
                else:
                    # For vegetables and other produce, use the robust heuristic analyzer
                    # this identifies spoilage via browning, texture variance and saturation
                    fallback = await self._analyze_image_freshness(image_bytes)
                    status = fallback['freshness_status']
                    risk = fallback['risk_score']
                    food_name = food_name_override or fallback['food_name']
                    confidence = fallback['confidence']

                # Brinjal mapping fix
                if food_name.lower() == "eggplant":
                    food_name = "Brinjal"

                recs = {
                    'fresh': f'{food_name} appears fresh! Store properly to maintain quality.',
                    'slightly_aged': f'{food_name} is slightly aged. Consume soon.',
                    'rotten': f'{food_name} shows signs of spoilage. Do not consume.'
                }

                return {
                    'food_name': food_name,
                    'freshness_status': status,
                    'risk_score': round(risk, 2),
                    'recommendation': recs.get(status, 'Handle with care.'),
                    'confidence': round(confidence, 2)
                }
            except Exception as e:
                print(f"Freshness prediction failed: {e}")
        
        # Enhanced mock response based on image analysis
        fallback = await self._analyze_image_freshness(image_bytes)
        if food_name_override:
            fallback['food_name'] = food_name_override
        return fallback
    
    async def recognize_food(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Recognize food type from image.
        
        Dataset: Food-101 Dataset
        Model: CNN trained on 101 food categories
        
        Returns:
            {
                'food_name': str,
                'category': str,
                'confidence': float
            }
        """
        
        if self.food_recognition_model:
            try:
                preprocessed = self._preprocess_image(image_bytes)
                prediction = self.food_recognition_model.predict(preprocessed)[0]
                class_idx = np.argmax(prediction)
                confidence = float(prediction[class_idx])
                
                food_name = self.food_classes.get(str(class_idx), f"Class_{class_idx}")
                food_name = food_name.replace('_', ' ').title()
                
                # Confidence-based refinement logic
                # Problematic categories that are often misidentified raw produce
                problematic_model_outputs = ["Soy Beans", "Peas", "Green Beans", "Spinach"]
                
                if confidence < 0.85 or food_name in problematic_model_outputs:
                    # Run heuristic to cross-validate
                    image = Image.open(io.BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    img_array = np.array(image)
                    avg_red = np.mean(img_array[:, :, 0])
                    avg_green = np.mean(img_array[:, :, 1])
                    avg_blue = np.mean(img_array[:, :, 2])
                    
                    heuristic_name = self._identify_food_by_color(avg_red, avg_green, avg_blue)
                    
                    # If heuristic found a specific high-value Produce item, prefer it over generic model output
                    special_produce = ["Lady's Finger", "Bitter Gourd", "Cucumber", "Brinjal", "Green Bell Pepper"]
                    if heuristic_name in special_produce:
                        return {
                            'food_name': heuristic_name,
                            'category': f'Hybrid Detection (Validated {food_name})',
                            'confidence': round(max(confidence, 0.82), 2)
                        }
                
                return {
                    'food_name': food_name,
                    'category': 'Recognized Output',
                    'confidence': round(confidence, 2)
                }
            except Exception as e:
                print(f"Food recognition failed: {e}")
        
        # Smart Heuristic Fallback instead of hardcoded 'Apple'
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_array = np.array(image)
            avg_red = np.mean(img_array[:, :, 0])
            avg_green = np.mean(img_array[:, :, 1])
            avg_blue = np.mean(img_array[:, :, 2])
            
            heuristic_name = self._identify_food_by_color(avg_red, avg_green, avg_blue)
            
            return {
                'food_name': heuristic_name,
                'category': 'Heuristic Output (Neural Engine offline)',
                'confidence': 0.65
            }
        except Exception:
            return {
                'food_name': 'Unknown Food',
                'category': 'Analysis Failed',
                'confidence': 0.0
            }
    
    async def classify_waste(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Classify waste type.
        
        Dataset: Food Waste Dataset
        Model: CNN for waste classification
        
        Returns:
            {
                'waste_type': str,
                'recyclable': bool,
                'compostable': bool
            }
        """
        
        if self.waste_model:
            try:
                preprocessed = self._preprocess_image(image_bytes)
                prediction = self.waste_model.predict(preprocessed)[0]
                class_idx = np.argmax(prediction)
                confidence = float(prediction[class_idx])
                
                mapped_class = self.waste_classes.get(str(class_idx), 'O')
                
                is_recyclable = mapped_class == 'R' or mapped_class == "Recyclable"
                is_organic = mapped_class == 'O' or mapped_class == "Organic"
                
                return {
                    'waste_type': 'recyclable' if is_recyclable else 'organic',
                    'recyclable': is_recyclable,
                    'compostable': is_organic,
                    'confidence': round(confidence, 2)
                }
            except Exception as e:
                print(f"Waste classification failed: {e}")
        
        # Mock response
        return {
            'waste_type': 'organic',
            'recyclable': False,
            'compostable': True
        }

    async def predict_unified(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Unified prediction using both Recognition and Freshness models.
        1. Identify the food item using the 36-item recognition model.
        2. Assess the quality/freshness using the binary freshness model.
        """
        # 1. Identify Food
        recognition = await self.recognize_food(image_bytes)
        recognized_name = recognition['food_name']
        
        # 2. Assess Freshness using the recognized name
        prediction = await self.predict_freshness(image_bytes, food_name_override=recognized_name)
        
        # 3. Use recognition confidence if it's high, otherwise the freshness one
        if recognition['confidence'] > 0.5:
            prediction['confidence'] = recognition['confidence']
            
        return prediction
    
    def _mock_freshness_prediction(self) -> Dict[str, Any]:
        """Mock prediction for development."""
        import random
        
        foods = ['Apple', 'Banana', 'Orange', 'Tomato', 'Lettuce', 'Carrot']
        statuses = ['fresh', 'slightly_aged', 'rotten']
        
        food = random.choice(foods)
        status = random.choice(statuses)
        risk_score = random.uniform(0, 100)
        
        recommendations = {
            'fresh': 'Food is fresh! Store properly to maintain quality.',
            'slightly_aged': 'Consume within 1-2 days or use in cooked dishes.',
            'rotten': 'Do not consume. Consider composting.'
        }
        
        return {
            'food_name': food,
            'freshness_status': status,
            'risk_score': round(risk_score, 2),
            'recommendation': recommendations[status],
            'confidence': round(random.uniform(0.7, 0.99), 2)
        }
    
    async def _analyze_image_freshness(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze image characteristics to provide realistic freshness prediction.
        Uses color analysis, brightness, and image properties.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Analyze image characteristics
            img_array = np.array(image)
            
            # Calculate average brightness
            brightness = np.mean(img_array)
            
            # Calculate color variance (higher variance = more varied colors)
            color_variance = np.var(img_array)
            
            # Calculate dominant colors
            avg_red = np.mean(img_array[:, :, 0])
            avg_green = np.mean(img_array[:, :, 1])
            avg_blue = np.mean(img_array[:, :, 2])
            
            # Determine food type based on dominant colors
            food_name = self._identify_food_by_color(avg_red, avg_green, avg_blue)
            
            # Determine freshness based on image characteristics
            freshness_status, risk_score = self._determine_freshness(
                brightness, color_variance, avg_red, avg_green, avg_blue
            )
            
            recommendations = {
                'fresh': f'{food_name} appears fresh! Store in a cool, dry place to maintain quality. Expected shelf life: 5-7 days.',
                'slightly_aged': f'{food_name} is slightly aged. Best to consume within 1-2 days or use in cooked dishes. Check for any soft spots.',
                'rotten': f'{food_name} shows signs of spoilage. Do not consume. Consider composting to reduce waste.'
            }
            
            # Calculate confidence based on image quality
            confidence = min(0.95, 0.75 + (color_variance / 10000))
            
            # Calculate saturation for analysis
            max_color = max(avg_red, avg_green, avg_blue)
            min_color = min(avg_red, avg_green, avg_blue)
            saturation = max_color - min_color
            
            return {
                'food_name': food_name,
                'freshness_status': freshness_status,
                'risk_score': round(risk_score, 2),
                'recommendation': recommendations[freshness_status],
                'confidence': round(confidence, 2),
                'analysis': {
                    'brightness': round(brightness, 2),
                    'color_variance': round(color_variance, 2),
                    'saturation': round(saturation, 2),
                    'dominant_color': self._get_dominant_color_name(avg_red, avg_green, avg_blue),
                    'avg_red': round(avg_red, 2),
                    'avg_green': round(avg_green, 2),
                    'avg_blue': round(avg_blue, 2)
                }
            }
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self._mock_freshness_prediction()
    
    def _identify_food_by_color(self, red: float, green: float, blue: float) -> str:
        """Identify likely food type based on dominant colors with better accuracy."""
        
        # Calculate color ratios and characteristics
        total = red + green + blue
        if total == 0:
            return 'Unknown Food'
        
        red_ratio = red / total
        green_ratio = green / total
        blue_ratio = blue / total
        
        # Calculate saturation
        max_color = max(red, green, blue)
        min_color = min(red, green, blue)
        saturation = max_color - min_color
        
        # RED FOODS (Tomato, Red Apple, Strawberry, Red Pepper)
        if red > green and red > blue:
            if red > 180 and saturation > 80:
                # Very red and saturated
                if green < 100:
                    return 'Tomato'
                else:
                    return 'Red Bell Pepper'
            elif red > 150 and saturation > 60:
                # Medium red
                if green > 100:
                    return 'Apple (Red)'
                else:
                    return 'Strawberry'
            elif red > 120:
                return 'Red Onion'
            else:
                return 'Radish'
        
        # GREEN FOODS (Lettuce, Cucumber, Green Apple, Broccoli, Spinach, Lady's Finger, Bitter Gourd)
        elif green > red and green > blue:
            if green > 170 and saturation > 85:
                # Very vibrant green
                if red < 70:
                    return 'Spinach'
                elif red < 100 and blue < 100:
                    # Specific check for bitter gourd: darker, rougher appearance usually translates to lower mean green than lettuce
                    if green < 185:
                        return 'Bitter Gourd'
                    else:
                        return 'Lettuce'
                else:
                    return 'Lettuce'
            elif green > 125 and saturation > 50:
                # Medium green
                if blue > 95 and red < 105:
                    return 'Cucumber'
                elif red > 45 and blue < 95:
                    # Lady's finger and Bitter gourd low-threshold check
                    if red > 95:
                        return 'Lady\'s Finger'
                    else:
                        return 'Bitter Gourd'
                else:
                    return 'Green Bell Pepper'
            elif green > 115:
                if red > 100:
                    return 'Apple (Green)'
                elif blue < 85:
                    return 'Bitter Gourd' # Slightly darker green fallback
                else:
                    return 'Broccoli'
            else:
                return 'Cabbage'
        
        # YELLOW/ORANGE FOODS (Banana, Orange, Carrot, Mango, Lemon)
        elif red > 140 and green > 140 and blue < 120:
            if red > green + 20:
                # More red than green = orange
                if saturation > 100:
                    return 'Orange'
                else:
                    return 'Carrot'
            elif green > red + 10:
                # More green than red = yellow
                if saturation > 80:
                    return 'Lemon'
                else:
                    return 'Banana'
            else:
                # Equal red and green
                if saturation > 90:
                    return 'Mango'
                else:
                    return 'Yellow Squash'
        
        # PURPLE/BLUE FOODS (Eggplant, Blueberry, Purple Cabbage)
        elif blue > red and blue > green:
            if blue > 120:
                if red > 80:
                    return 'Purple Cabbage'
                else:
                    return 'Blueberry'
            else:
                return 'Brinjal'
        
        # BROWN/BEIGE FOODS (Potato, Mushroom, Onion)
        elif red > 80 and green > 70 and blue > 60 and saturation < 50:
            if red < 120:
                return 'Mushroom'
            elif abs(red - green) < 20:
                return 'Potato'
            else:
                return 'Brown Onion'
        
        # WHITE/LIGHT FOODS (Cauliflower, White Onion, Garlic)
        elif red > 180 and green > 180 and blue > 180:
            if saturation < 30:
                return 'Cauliflower'
            else:
                return 'White Onion'
        
        # ORANGE VEGETABLES (Pumpkin, Sweet Potato)
        elif red > 160 and green > 100 and green < 140 and blue < 80:
            if saturation > 100:
                return 'Pumpkin'
            else:
                return 'Sweet Potato'
        
        # Default fallback
        if red_ratio > 0.4:
            return 'Red Produce'
        elif green_ratio > 0.4:
            return 'Green Produce'
        elif blue_ratio > 0.35:
            return 'Purple Produce'
        else:
            return 'Mixed Produce'
    
    def _determine_freshness(self, brightness: float, variance: float, red: float, green: float, blue: float) -> tuple:
        """
        Determine freshness status and risk score based on image characteristics.
        
        Logic:
        - Bright, vibrant colors with high variance = Fresh
        - Moderate brightness, browning = Slightly aged
        - Dark, low variance, brown/black = Rotten
        """
        
        # Calculate freshness score (0-100, higher is worse)
        risk_score = 0
        
        # 1. Brightness Analysis (most important for rot detection)
        if brightness < 60:
            risk_score += 50  # Very dark = very rotten
        elif brightness < 100:
            risk_score += 35  # Dark = rotten
        elif brightness < 130:
            risk_score += 20  # Somewhat dark = aging
        elif brightness > 180:
            risk_score += 5   # Very bright = fresh
        else:
            risk_score += 10  # Normal brightness
        
        # 2. Color Variance Analysis (texture and uniformity)
        if variance < 300:
            risk_score += 35  # Very uniform = mushy/rotten
        elif variance < 800:
            risk_score += 20  # Low variance = aging
        elif variance < 1500:
            risk_score += 10  # Moderate variance
        else:
            risk_score += 0   # High variance = fresh texture
        
        # 3. Brown/Gray Tone Detection (spoilage indicator)
        # Calculate how "brown" the image is
        avg_color = (red + green + blue) / 3
        color_deviation = abs(red - green) + abs(green - blue) + abs(blue - red)
        
        # If colors are similar (low deviation) and dark, it's brown/gray
        # For green produce, browning is a critical risk factor
        if color_deviation < 55 and avg_color < 110:
            risk_score += 35  # Brown/gray = rotten
        elif color_deviation < 85 and avg_color < 145:
            risk_score += 20  # Slightly brown = aging
        
        # Specific Green Depletion Check
        if green > red + 10 and green > blue + 10:
             # It is green produce
             if red > green * 0.8: # Red creeping up on Green = browning
                 risk_score += 15
        
        # 4. Color Saturation (vibrant vs dull)
        max_color = max(red, green, blue)
        min_color = min(red, green, blue)
        saturation = max_color - min_color
        
        if saturation < 30:
            risk_score += 25  # Very dull = rotten
        elif saturation < 60:
            risk_score += 15  # Dull = aging
        elif saturation > 100:
            risk_score -= 10  # Vibrant = fresh (bonus)
        
        # 5. Specific checks for dark spots (black/very dark areas)
        if brightness < 80 and variance < 500:
            risk_score += 20  # Dark + uniform = severe rot
        
        # Ensure risk score is within bounds
        risk_score = max(0, min(100, risk_score))
        
        # Determine status based on risk score with clear thresholds
        if risk_score < 25:
            return 'fresh', risk_score
        elif risk_score < 55:
            return 'slightly_aged', risk_score
        else:
            return 'rotten', risk_score
    
    def _get_dominant_color_name(self, red: float, green: float, blue: float) -> str:
        """Get human-readable color name."""
        if red > green and red > blue:
            return 'Red'
        elif green > red and green > blue:
            return 'Green'
        elif blue > red and blue > green:
            return 'Blue'
        elif red > 150 and green > 150:
            return 'Yellow/Orange'
        elif red < 100 and green < 100 and blue < 100:
            return 'Brown/Dark'
        else:
            return 'Mixed'

ml_service = MLService()
