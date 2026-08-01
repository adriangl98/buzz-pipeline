"""Laredo Dental FAQ knowledge base — bilingual dental office information."""
import re


class FAQ:
    """Answer common dental office questions in English and Spanish.

    Uses keyword-based matching with language detection to route
    questions to the appropriate language answer.
    """

    # ── knowledge base ────────────────────────────────────────────────

    ANSWERS = {
        "hours": {
            "en": (
                "Our office hours are Monday through Friday, 8:00 AM to 5:00 PM. "
                "We are closed on weekends. For emergencies outside these hours, "
                "please call our after-hours line."
            ),
            "es": (
                "Nuestro horario es de lunes a viernes, de 8:00 AM a 5:00 PM. "
                "Estamos cerrados los fines de semana. Para emergencias fuera de "
                "este horario, llame a nuestra línea de after-hours."
            ),
        },
        "location": {
            "en": (
                "We are located at 123 San Bernardo Ave, Laredo, TX 78040. "
                "Free parking is available behind the building. "
                "We're across the street from the H-E-B on San Bernardo."
            ),
            "es": (
                "Estamos ubicados en 123 San Bernardo Ave, Laredo, TX 78040. "
                "Hay estacionamiento gratuito detrás del edificio. "
                "Estamos frente al H-E-B de San Bernardo."
            ),
        },
        "insurance": {
            "en": (
                "We accept most major dental insurance plans including "
                "Delta Dental, Aetna, Cigna, MetLife, Guardian, and Blue Cross Blue Shield. "
                "We also offer flexible payment plans for uninsured patients. "
                "Please bring your insurance card to your first visit."
            ),
            "es": (
                "Aceptamos la mayoría de los seguros dentales incluyendo "
                "Delta Dental, Aetna, Cigna, MetLife, Guardian, y Blue Cross Blue Shield. "
                "También ofrecemos planes de pago flexibles para pacientes sin seguro. "
                "Por favor traiga su tarjeta de seguro a su primera visita."
            ),
        },
        "services": {
            "en": (
                "We offer a full range of dental services: routine cleanings and exams, "
                "fillings and crowns, teeth whitening, braces and orthodontics, "
                "root canals, extractions, dental implants, and pediatric dentistry. "
                "Contact us for a consultation!"
            ),
            "es": (
                "Ofrecemos una gama completa de servicios dentales: limpiezas y "
                "exámenes de rutina, rellenos y coronas, blanqueamiento dental, "
                "frenos y ortodoncia, endodoncias, extracciones, implantes dentales, "
                "y odontología pediátrica. ¡Contáctenos para una consulta!"
            ),
        },
        "new_patient": {
            "en": (
                "Welcome! For new patients, we'll need your name, phone number, "
                "and preferred appointment time. I can take that information now "
                "and our staff will call you to confirm within 24 hours."
            ),
            "es": (
                "¡Bienvenido! Para pacientes nuevos, necesitamos su nombre, "
                "número de teléfono y horario preferido para la cita. "
                "Puedo tomar esa información ahora y nuestro personal le llamará "
                "para confirmar dentro de 24 horas."
            ),
        },
    }

    # ── keyword → topic mapping ───────────────────────────────────────

    KEYWORDS = {
        "hours": {
            "en": ["hour", "open", "close", "schedule", "time", "monday", "friday", "weekend"],
            "es": ["horario", "hora", "abierto", "cerrado", "lunes", "viernes", "fin de semana"],
        },
        "location": {
            "en": ["where", "located", "address", "location", "direction", "parking"],
            "es": ["donde", "ubicado", "dirección", "direccion", "ubicacion", "estacionamiento", "parking"],
        },
        "insurance": {
            "en": ["insurance", "accept", "plan", "coverage", "delta", "aetna", "cigna", "metlife", "pay"],
            "es": ["seguro", "aseguranza", "aceptan", "cobertura", "plan dental", "pago"],
        },
        "services": {
            "en": ["service", "offer", "cleaning", "filling", "crown", "braces", "whitening", "root canal", "implant", "extraction"],
            "es": ["servicio", "ofrecen", "limpieza", "relleno", "corona", "frenos", "blanqueamiento", "endodoncia", "implante", "extracción"],
        },
        "new_patient": {
            "en": ["new patient", "first time", "first visit", "first appointment", "never been", "new here"],
            "es": ["nuevo paciente", "primera vez", "primera visita", "primera cita", "nunca he ido", "nuevo aquí"],
        },
    }

    # ── public API ─────────────────────────────────────────────────────

    def ask(self, question: str) -> str | None:
        """Answer a question about the dental office.

        Args:
            question: The patient's question in English or Spanish.

        Returns:
            Answer string in matching language, or None if no match.
        """
        topic = self._classify(question)
        if topic is None:
            return None

        lang = self._detect_language(question)
        return self.ANSWERS[topic][lang]

    # ── private helpers ────────────────────────────────────────────────

    def _classify(self, question: str) -> str | None:
        """Match question to a topic using keyword scoring."""
        lower = question.lower()
        scores = {}

        for topic, lang_keywords in self.KEYWORDS.items():
            score = 0
            for lang, keywords in lang_keywords.items():
                for kw in keywords:
                    if kw in lower:
                        score += 1
            if score > 0:
                scores[topic] = score

        if not scores:
            return None

        return max(scores, key=lambda k: scores[k])

    @staticmethod
    def _detect_language(text: str) -> str:
        """Detect if text is primarily Spanish."""
        spanish_markers = [
            "hola", "gracias", "cita", "por favor", "¿", "ñ",
            "buenos", "buenas", "tardes", "días", "horario",
            "ubicado", "ubicación", "dirección", "estacionamiento",
            "seguro", "aseguranza", "servicio", "ofrecen",
            "limpieza", "relleno", "frenos", "blanqueamiento",
        ]
        lower = text.lower()
        for marker in spanish_markers:
            if marker in lower:
                return "es"
        return "en"
