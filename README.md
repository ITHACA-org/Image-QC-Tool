# Image QC Tool - BETA version

## Funzionalità principali 

Il tool svolge i seguenti compiti:

1) Processamento dell'immagine
2) Generazione del footprint in formati .shp, .kml e .gdb
3) Compilazione di A0_source & A2_image_footprint_a
4) Compilazione del Quality Check in formato word

## Processamenti supportati

I processamenti dell'immagine supportati sono: 

- Composite bands (in caso di Sentinel-2, Landsat8-9)
- Mosaicatura (qualora più di un input sia fornito al parametro "Image/Tiles")
- Riproiezione (qualora il sistema di riferimento dell'AOI e quello dell'immagine non coincidessero)
- Conversione in formato .tif dell'input

Non sono invece implementati processamenti per le immagini SAR; qualora si lavori con questo tipo di immagine bisognerà fornire direttamente il .tif processato al parametro "Image/Tiles"

## Funzionamento del Tool e parametri
