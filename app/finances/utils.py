
def calcul_deduction(montant, pourcentage):
    """
    Calcule la déduction d'un pourcentage donné sur un montant.
    
    Args:
        montant (float): Le montant initial
        pourcentage (float): Le pourcentage à déduire (ex: 10 pour 10%)
    
    Returns:
        tuple: (montant_apres_deduction, montant_preleve)
    """
    montant_preleve = montant * (pourcentage / 100)
    montant_apres_deduction = montant - montant_preleve
    
    return montant_apres_deduction, montant_preleve


