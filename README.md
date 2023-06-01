Implementační dokumentace k 2. úloze do IPP 2022/2023  
Jméno a příjmení: Jakub Kontrík  
Login: xkontr02  

## Implementácia
Skript sa skladá z 9 modulov:
- `interpret.py` - hlavný modul, spracovava nacitane argumenty volá xml validátor ukladá labely a volá továreň triedu na vyvorenie inštrukcií zo zadaného vstupu
- `xml_validator.py` - modul, ktorý validuje zadaný xml vstup
- `arg_parse.py` - modul, ktorý spracováva argumenty príkazoveho riadku
- `error.py` - modul, ktorý obsahuje číselne kódy chýb
- `factory.py` - modul, ktorý obsahuje triedu, ktorá vytvára inštrukcie
- `instruction.py` - modul, ktorý obsahuje rodičovskú triedu, jej dediacich potomkov, triedu pre argumenty a triedu pre vlastný typ nil
- `interpret_class.py` - modul, ktorý riadi vykonávanie inštrukcií
- `stack.py` - modul, ktorý obsahuje triedu pre vlastný zásobník
- `frame.py` - modul, ktorý obsahuje triedu reprezentujúcu rámec

### Priebeh programu
Telo `interpret.py` sa nachadza v "maine" najprv sa vytvorí inštancia triedy `ArgumentParser` v ktorej konštruktore sa načítavajú argumenty. Na načitávanie sa používa upravená trieda argparse.ArgumentParser, ktorá ma zmenenú metódu na spravné končiace kódy. Z objektu sa potom ziskajú argumenty a zvalidujú sa. Následuje vytvorenie objektu triedy `XmlValidator`  sa zvaliduje xml vstup. Ďalej sa upravený strom prejde a načítajú sa náveštia. Potom sa vytvorí objekt triedy `Factory` a pomocou metódy `get_instruction` sa načítavajú inštrukcie a ukladajú do zoznamu. Každá inštrukcia zo špecifikácie ma vlastnú triedu, ktorá dedí z rodičovskej triedy `Instruction`. Takisto sa načítavajú argumenty pre každú inštrukciu. Finálnym krokom je vytvorenie objektu triedy `Interpret` a vykonanie inštrukcií pomocou metódy `run`. `Interpret` je tiež nositeľom "globálnych" premenných potrebné na spracovávanie inštrukcií(call_stack, rámce,...). `Run` metóda iteruje načítanými inštrukciami a vykonáva ich postupne. Ak narazí program na náveštie alebo skok tak sa iterátor zmení na potrebný index v poli inštrukcií.

### OOP návrh
Môj návrh sa odvíja z navrhového vzoru `Fatctory`, čiže továreň, ktorá vytvára inštrukcie. Kaźdá inštrukcia je generalizáciou materskej triedy `Instruction`, ktorá obsahuje metódu na vykonanie danej inštrukcie. Inštrukcie obsahujú aj objekty triedy `Argument`. Hlavný tok programu, teda "main" komunikuje a používa továreň a `Interpret`.

### Prípadné rozšírenia

- float: pre rozšírenie na float by sa musel vytvoriť nový typ argumentu, upraviť existujúce aritmetické inštrukcie, aby podporovali aj float a vytvoriť nové metódy inštrukcií pre prácu s float.
- stack: pre rozšírenie na stack stačilo vytvoriť nové inštrukcie, ktoré by pracovali s datovým stackom, a položkami na ňom.
- stats: pre rozšírenie na stats by sa musela vytvoriť nová trieda, ktorá by obsahovala uschovavala potrebné data a spracovávala ich. Potom by sa museli pridat nové možnosti spúštacich argumentov.