"""Compatibilité pour les anciens imports de ``kpata.brief``.

Le schéma est défini dans :mod:`kpata.schema` et le moteur dans
:mod:`kpata.completude`.
"""
from .completude import (SEUIL, SEUIL_PROPOSE, champs_manquants, completude,
                        pret_pour_generation)
from .schema import (BASE, CHAMPS, INTENTS, MEDIAS, OBLIGATOIRES, POIDS,
                    POIDS_PAR_INTENTION, SOUHAITES, TONS, nouveau_brief)
