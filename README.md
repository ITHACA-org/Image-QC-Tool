# Image QC Tool - BETA version

## Funzionalità principali 

Il tool svolge i seguenti compiti:

1) Processamento dell'immagine
2) Generazione del footprint in formati .shp, .kml e .gdb
3) Compilazione di A0_source & A2_image_footprint_a
4) Compilazione del Quality Check in formato word

**Il tool si lancia PERENTORIAMENTE da template**

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

1) EMSR number: Il codice dell'attivazione. Questo parametro si compila **automaticamente**, poichè il tool leggerà tale codice direttamente dall'attribute table dell'AOI.
  
2) AOI number:  Il codice dell'Area Of Interest. Questo parametro si compila **automaticamente**, poichè il tool leggerà tale codice direttamente dall'attribute table dell'AOI.
  
3) Product Type: Tipologia di prodotto (FEP, DEL, DELMONIT,...). Questo parametro si compila **automaticamente**, poichè il tool leggerà tale codice direttamente dall'attribute table dell'AOI. Qualora il valore di questo parametro e la tipologia di mappa riportata nel template non coincidessero, apparirà un messaggio di warning affianco al parametro chiedendovi di sistemare questa incongruenza.

4) Sensor: Sensore di acquisizione dell'immagine. Lo user dovrà selezionare il sensore dalla lista delle opzioni disponibili. Questo tool è capace di leggere la data di acquisizione entrando direttamente nei metadati della cartella raw del sensore, ma questa funzionalità è disponibile solo per alcune tipologie di sensore (ovvero quelli che vengono impiegati nel 99% delle attivazioni). Qualora venisse selezionato un sensore per cui questa funzionalità non è disponibile un messaggio di warning apparirà di fianco al parametro.

5) Raw sensor folder: Qui bisogna fornire la cartella raw del sensore (ovvero così come viene scaricata dall'RRD/FTP). La cartella **DEVE ESSERE UNZIPPATA** in tutti i suoi livelli interiori. Non importa se usando un programma come 7zip vengono a crearsi delle cartelle di cartelle (ovvero un effetto matriosca), l'importante è che **non** ci siano files zippati dentro la cartella. Questo parametro scomparirà in caso nel parametro precedente (i.e. "Sensor") venga selezionato un sensore che non possiede una cartella raw (ad esempio la ESRI) o un satellite per cui non è disponibile la lettura automatica dei metadati. Se verrà fornita una cartella Sentinel-2 o Landsat, il tool procederà automaticamente a produrre il composite band della cartella. Se più di una cartella Sentinel-2 o Landsat sarà fornita, il tool produrrà il composite band di ogni cartella e mosaicherà le immagini risultanti.

6) Image/Tiles: In questo parametro verrà inserita l'immagine (o i tiles) su cui verrà dimensionato il footprint. Per quasi tutti i sensori ottici questo campo verrà compilato automaticamente, dato che il tool è capace di trovare da solo i files all'interno della cartella raw. Questo campo accetta i formati .tif, .jp2, .til, e .DIM. Al contrario, come già specificato, qualora si lavori con un sensore SAR bisognerà caricare manualmente in questo campo l'immagine .tif già processata. Se più di un tile verrà caricato in questo campo, il tool procederà automaticamente alla mosaicatura di tutti i tiles indicati; inoltre, qualora uno o più tiles si trovassero in un CRS diverso da quello dell'attivazione (ovvero quello dell'AOI), verrà automaticamente attivata una procedura di riproiezione. E' importante specificare che, nonostante la compilazione automatica, è sempre possibile cancellare i files di input trovati dal tool e caricare manualmente quelli di proprio interesse. ESEMPIO: quando una cartella WorldView viene caricata, il tool trova automaticamente i files .til, ma è sempre possibile rimuoverli e caricare i diversi .tif presenti all'interno della cartella. Questo parametro scompare qualora venga selezionato come sensore Sentinel-2 o Landsat.
