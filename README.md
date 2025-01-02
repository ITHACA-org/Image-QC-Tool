# Image QC Tool - BETA version

## Funzionalità principali 

Il tool svolge i seguenti compiti:

1) Processamento dell'immagine
2) Generazione del footprint in formati .shp, .kml e .gdb
3) Compilazione di A0_source & A2_image_footprint_a
4) Compilazione del Quality Check in formato word

**Il tool si lancia perentoriamente da template**

## Processamenti supportati

I processamenti dell'immagine supportati sono: 

- Composite bands (in caso di Sentinel-2, Landsat8-9)
- Mosaicatura (qualora più di un input sia fornito al parametro "Image/Tiles")
- Riproiezione (qualora il sistema di riferimento dell'AOI e quello dell'immagine non coincidessero)
- Conversione in formato .tif dell'input

**Non** sono invece implementati processamenti per le immagini SAR; qualora si lavori con questo tipo di immagine bisognerà fornire direttamente il .tif processato al parametro "Image/Tiles"

## Funzionamento del Tool e parametri

### Controllare i messaggi a schermo

Come premessa, è altamente consigliato, durante il runtime, aprire i messaggi che il tool manda a schermo cliccando su "View Details". Infatti, considerando la grande varietà di sensori e casistiche che si possono presentare, sarebbe difficile (e prolisso) racchiudere in questa guida tutti i potenziali outputs e processamenti che possono avvenire. Tuttavia i messaggi stampati a schermo sono appositamente generati per guidare lo user: essi contengono i percorsi ai quali vengono generati i prodotti, nonchè una indicazione su quali processamenti sono stati svolti (è stato/non è stato effettuato il mosaico, è avvenuta o meno la riproiezione di uno o più tiles, etc...)

### Parametri

Si fornirà ora una lista dei parametri accompagnata dalle principali funzioni del tool associate a ciascun parametro:

1) 
