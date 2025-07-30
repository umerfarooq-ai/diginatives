import os
import base64
import google.generativeai as genai
from typing import Dict, Any
import json
import re
from dotenv import load_dotenv

load_dotenv()


class AISkinAnalysisService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_skin_image(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze skin image using Google Gemini Vision API
        """
        try:
            # Create the prompt for skin analysis
            prompt = """
            Analyze this skin image and provide a comprehensive, non-medical cosmetic skincare assessment.

            Please return the results in the following structured JSON format:

            {
            "treatmentProgram": {
                "hydration": float (0-100),
                "elasticity": float (0-100),
                "complexion": float (0-100),
                "texture": float (0-100)
            },
            "skinHealthMatrix": {
                "pores": float (0-100),
                "underEyeAppearance": float (0-100), 
                "blemishes": float (0-100),
                "spots": float (0-100),
                "redness": float (0-100),
                "oiliness": float (0-100),
                "fineLines": float (0-100),
                "texture": float (0-100)
            },
            "amRoutine": "string with steps (1. cleanser, 2. serum, ...)",
            "pmRoutine": "string with steps",
            "nutritionRecommendations": "short string of general dietary advice",
            "productRecommendations": "list of product types, not brands",
            "ingredientRecommendations": "list of common skincare ingredients"
            }

            Guidelines:
            - This is not a medical diagnosis.
            - Do not mention or infer medical conditions (e.g., acne severity, skin disease).
            - Assume the user is asking for a **cosmetic analysis** and routine suggestions based on visible skin tone, hydration, oiliness, etc.
            - Use practical, commonly known skincare advice.
            - Return only the JSON. Do not include explanations or text outside the JSON.
            """

            # Convert base64 to bytes for Gemini
            image_bytes = base64.b64decode(image_base64)

            # Call Gemini Vision API
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ])

            # Get the response content
            ai_response = response.text
            print("Gemini RAW OUTPUT:\n", ai_response)

            # Try to parse as JSON first
            try:
                # Extract JSON from the response if it's wrapped in markdown
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object in the response
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = ai_response

                result = json.loads(json_str)
                return result

            except json.JSONDecodeError:
                print("JSON parsing failed, using text parser")
                return self._parse_field_lines(ai_response)

        except Exception as e:
            print(f"❌ Error in Gemini analysis: {e}")
            print("🔄 Using fallback response...")
            return self._get_error_response(str(e))

    def _parse_field_lines(self, text: str) -> Dict[str, Any]:
        """
        Parse AI response text and extract structured data
        """
        try:
            result = {
                "treatmentProgram": {
                    "hydration": 70.0,
                    "elasticity": 65.0,
                    "complexion": 75.0,
                    "texture": 70.0
                },
                "skinHealthMatrix": {
                    "pores": 60.0,
                    "underEyeAppearance": 50.0,
                    "blemishes": 40.0,
                    "spots": 0.0,
                    "redness": 45.0,
                    "oiliness": 65.0,
                    "fineLines": 40.0,
                    "texture": 70.0
                },
                "amRoutine": "1. Gentle cleanser\n2. Vitamin C serum\n3. Moisturizer\n4. SPF sunscreen",
                "pmRoutine": "1. Double cleanse\n2. Retinol serum\n3. Moisturizer",
                "nutritionRecommendations": "Stay hydrated, eat antioxidant-rich foods, reduce sugar intake",
                "productRecommendations": "Gentle cleanser, Vitamin C, Retinol, Moisturizer, SPF",
                "ingredientRecommendations": "Hyaluronic acid, Vitamin C, Retinol, Niacinamide"
            }

            # Try to extract scores from the text
            lines = text.split('\n')
            for line in lines:
                line = line.strip().lower()

                # Extract hydration score
                if 'hydration' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["hydration"] = score

                # Extract elasticity score
                elif 'elasticity' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["elasticity"] = score

                # Extract complexion score
                elif 'complexion' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["complexion"] = score

                # Extract texture score
                elif 'texture' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["texture"] = score

                # Extract skin health matrix scores
                elif any(keyword in line for keyword in
                         ['pores', 'under eye', 'blemishes', 'spots', 'redness', 'oiliness', 'fine lines']):
                    for keyword in ['pores', 'under eye', 'blemishes', 'spots', 'redness', 'oiliness', 'fine lines']:
                        if keyword in line:
                            score = self._extract_score_from_line(line)
                            if score is not None:
                                if keyword == 'under eye':
                                    result["skinHealthMatrix"]["underEyeAppearance"] = score
                                elif keyword == 'fine lines':
                                    result["skinHealthMatrix"]["fineLines"] = score
                                elif keyword == 'blemishes':
                                    result["skinHealthMatrix"]["blemishes"] = score
                                else:
                                    result["skinHealthMatrix"][keyword] = score
                            break

            return result

        except Exception as e:
            print(f"Text parsing failed: {e}")
            return self._get_fallback_response()

    def _extract_score_from_line(self, line: str) -> float:
        """
        Extract a score (0-100) from a text line
        """
        try:
            # Look for numbers in the line
            numbers = re.findall(r'\d+(?:\.\d+)?', line)
            for num in numbers:
                score = float(num)
                if 0 <= score <= 100:
                    return score
            return None
        except:
            return None

    def _get_fallback_response(self) -> Dict[str, Any]:
        """
        Return a fallback response if AI analysis fails
        """
        print("📋 Returning fallback response for testing")
        return {
            "treatmentProgram": {
                "hydration": 70.0,
                "elasticity": 65.0,
                "complexion": 75.0,
                "texture": 70.0
            },
            "skinHealthMatrix": {
                "pores": 60.0,
                "underEyeAppearance": 50.0,
                "blemishes": 40.0,
                "spots": 0.0,
                "redness": 45.0,
                "oiliness": 65.0,
                "fineLines": 40.0,
                "texture": 70.0
            },
            "amRoutine": "FALLBACK: Basic skincare routine (AI analysis failed)",
            "pmRoutine": "FALLBACK: Basic evening routine (AI analysis failed)",
            "nutritionRecommendations": "FALLBACK: General nutrition advice (AI analysis failed)",
            "productRecommendations": "FALLBACK: Basic products (AI analysis failed)",
            "ingredientRecommendations": "FALLBACK: Common ingredients (AI analysis failed)",
            "fallback_message": "⚠️ AI ANALYSIS FAILED - This is fallback data for testing"
        }

    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Return error response with actual error message
        """
        print(f"📋 Returning error response: {error_message}")
        return {
            "error": True,
            "error_message": f"AI Analysis Failed: {error_message}",
            "treatmentProgram": {},
            "skinHealthMatrix": {},
            "amRoutine": "",
            "pmRoutine": "",
            "nutritionRecommendations": "",
            "productRecommendations": "",
            "ingredientRecommendations": ""
        }

    def _convert_to_string(self, value) -> str:
        """
        Convert value to string, handling both strings and lists
        """
        if isinstance(value, list):
            return ", ".join(value)
        elif isinstance(value, str):
            return value
        else:
            return str(value) 