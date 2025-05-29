"""
Základní testy pro AI-agent-Ntier projekt.
"""

def test_example():
    """Základní test, který vždy projde."""
    assert True

def test_project_structure():
    """Test ověřující základní strukturu projektu."""
    import os
    
    # Kontrola existence klíčových adresářů
    assert os.path.isdir("src"), "Adresář 'src' nenalezen"
    assert os.path.isdir("src/memory_agent"), "Adresář 'src/memory_agent' nenalezen"
    
    # Kontrola existence klíčových souborů
    assert os.path.isfile("requirements.txt"), "Soubor 'requirements.txt' nenalezen"
    assert os.path.isfile("langgraph.json"), "Soubor 'langgraph.json' nenalezen"
