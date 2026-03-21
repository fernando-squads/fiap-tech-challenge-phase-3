class PatientRepository:

    def __init__(self):
        # mock (pode trocar por DB depois)
        self.patients = {
            "1": {
                "idade": 65,
                "sexo": "Masculino",
                "condicoes": ["diabetes", "hipertensão"],
                "medicamentos": ["metformina"]
            }
        }

    def get_patient(self, patient_id):
        patient = self.patients.get(patient_id, {})

        return f"""
Idade: {patient.get("idade")}
Sexo: {patient.get("sexo")}
Condições: {", ".join(patient.get("condicoes", []))}
Medicamentos: {", ".join(patient.get("medicamentos", []))}
"""