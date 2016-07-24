Autor: Marina Speranskaya

Hier findet ihr das Skript zur Kontrolle einer MRL. Damit es fehlerfrei ausgeführt wird, muss sich auch die Grammatikdatei "cfg.txt" in demselben Ordner befinden.


Um eine MRl auf Korrektheit zu überprüfen, braucht ihr folgende Schritte zu machen:

	import my_cfg_set as cfg
	parser = cfg.EarleyParser()
	
	grammar_file = "cfg.txt"
	gr = cfg.Grammar(grammar_file) #NEU: Defaultmäßig wird "cfg.txt" benutzt
	parser.set_grammar(gr)

	output = parser.parse_mrl(mrl)

	
Danach wird in der Variable output der Wahrheitswert gespeichert, den die Methode parse_mrl zurückliefert. Um es euch anzuschauen, könnt ihr die Funktion demo() in der Datei ausführen.

P.S. Im Moment kann die Methode ziemlich lange brauchen, um eine MRL zu bearbeiten. Ich werde dort noch einiges optimieren. Allerdings sollte das Programm korrekte Ergebnisse liefern. Wenn ihr merkt, dass es nicht stimmt, sagt es mir :) 
