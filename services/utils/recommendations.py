from typing import List, Dict

def generate_recommendations(values: Dict) -> List[str]:
    """
    values: {"pulse": int, "blood_pressure": int, "temperature": float, "weight": float, "height": float}
    height in cm, weight in kg.
    """
    recs: List[str] = []

    pulse = values.get("pulse")
    bp = values.get("blood_pressure")
    temp = values.get("temperature")
    weight = values.get("weight")
    height = values.get("height")

    # BMI
    bmi = None
    if height is not None and weight is not None and height > 0 and weight > 0:
        h = height / 100.0
        bmi = round(weight / (h * h), 1)

    # Pulse
    if pulse is not None:
        if pulse > 100:
            recs.append(
                "Pulse is elevated (>100). Rest 5–10 min, do deep breathing, limit caffeine. "
                "If it lasts >24 h or with chest pain/shortness of breath — see a doctor."
            )
        elif pulse < 50:
            recs.append(
                "Pulse is low (<50). If you’re not a trained athlete and feel weak/dizzy — consult a doctor."
            )
        else:
            recs.append("Pulse is within normal resting range.")

    # Blood pressure (single value, mmHg)
    if bp is not None:
        if bp >= 180:
            recs.append("Very high blood pressure (≥180). This is an emergency — seek urgent care.")
        elif bp >= 140:
            recs.append("High blood pressure (≥140). Limit salt/alcohol, measure regularly, book a GP visit.")
        elif bp <= 90:
            recs.append("Low blood pressure (≤90). Hydrate, stand up slowly, monitor for dizziness.")
        else:
            recs.append("Blood pressure is close to normal.")

    # Temperature
    if temp is not None:
        if temp >= 40:
            recs.append("High fever (≥40°C). Seek immediate medical attention.")
        elif temp >= 38:
            recs.append("Fever (≥38°C). Drink more water, rest; antipyretic if needed. If >48 h — see a doctor.")
        elif temp >= 37.5:
            recs.append("Low-grade fever (37.5–37.9°C). Rest, hydrate, monitor symptoms.")
        else:
            recs.append("Temperature is normal.")

    # BMI tips
    if bmi is not None:
        if bmi < 18.5:
            recs.append(f"BMI {bmi}: underweight. Increase calories (protein/healthy fats); consider a dietitian.")
        elif bmi < 25:
            recs.append(f"BMI {bmi}: normal. Maintain 150 min/week activity and a balanced diet.")
        elif bmi < 30:
            recs.append(f"BMI {bmi}: overweight. Cut sugar/ultra-processed foods; add 7–10k steps/day.")
        else:
            recs.append(f"BMI {bmi}: obesity. A supervised weight-loss plan is recommended.")

    # General gentle advice
    recs.append("Drink 6–8 glasses of water daily, sleep 7–9 hours, and take 5–10 min movement breaks each hour.")

    return recs
