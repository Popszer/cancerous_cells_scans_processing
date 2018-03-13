### R�union du 29 d�cembre 2018 avec Thomas
La r�union a permis d'affiner les sp�cifications pour le pipeline � d�ployer.
En entr�e on fournit un dossier de donn�es patients avec l'architecture suivante : (que l'on retrouve dans le jeu de donn�es fourni par Thomas)
�	Un dossier de donn�es contenant des dossiers patients sous forme xxx-xxx (x �tant un digit entre 0 et 9)
�	Dans chaque dossier patient on retrouve toujours la m�me architecture : un dossier dcm contenant la pile de dicom et un ou plusieurs dossiers contenant les masques not�s l1, l2, etc, associ�s � chaque l�sion du patient. 
�	Dans chaque dossier de l�sion, on retrouve trois masques : le kmean sous forme de .tif, un dossier pour le masque 2.5 (pile de masque) et un dossier pour le masque 40 (pile de masque) NB: ces deux derniers (2.5 et 40) peuvent �tre sous forme de .tiff et non en pile si ils ont �t� corrig�s (axe z invers� et ajout de couches dans la pile).
Le vendredi 29 janvier apr�s-midi, nous pr�sentons � Thomas un pipe qui permet de traiter un jeu de plusieurs donn�es patients avec pour output une structure qui associe � chaque l�sions d'un patient les caract�ristiques extraites de pyradiomics.
Informations suppl�mentaires pour la mise en place du pipeline :
-> Pour chaque l�sion d'un patient, on forme un masque par la m�thode du vote majoritaire � partir des 3 masques : 2.5, 40 et kmean. (M�thode du vote majoritaire seulement dans un premier temps, pas de STAPLE). Nous nous sommes inspir�s du code .py de Thomas pour le vote majoritaire.
-> Le masque r�sultant du vote majoritaire est fourni, avec la pile de dicom du patient correspondant, en entr�e � pyradiomics pour extraire les features.
-> On oublie dans un premier temps la technique de crop (r�duction de dimension) qui �tait r�alis� dans les scripts fiji : on va ici fournir les piles enti�res.
-> L'output devra �tre une structure de donn�es permettant d'extraire facilement les caract�ristiques obtenues par pyradiomics pour chaque l�sion de chaque patient.
Une fois ce pipeline fonctionnel et valid� par Thomas, nous organiserons une r�union avec Diana pour attaquer la partie machine learning.

---------------------------
### R�union du mercredi 24 janvier 2018 avec Thomas
Objectif : Validation du pipe de pr�-traitements des donn�es patients pour l'obtention de caract�ristiques des l�sions.
Probl�me pour faire tourner le script sur notre PC portable.
Information suppl�mentaire : les piles de DCM doivent �tre pr�-trait�es pour pouvoir �tre en unit� SUV/Bequerel standardis�e.


---------------------------
### R�union du lundi 29 janvier 2018 avec Diana et Thomas
Objectifs
#1 Pr�sentation du pipe fonctionnel de pr�-traitement
#2 S�lection des features � extraire pour comparaison de r�sultats
#3 R�fl�chir au choix du mod�le de machine learning
--- R�sum�
Points d'int�r�ts
- Pipe de pr�-traitement
Effectuer la conversion, par patient et pour chacune des slices dicom, dans l'unit� standardis�e en r�cup�rant la valeur li�e � la bonne balise dans les slices (r�f�rences des balises dans le code Fiji de Thomas).
Pr�-traitement scalable mais penser � exporter le code en .py pour contourner des limitations de ressources des notebooks lorsque jeu de donn�es en situation r�elle (>100Go)
- Extraction de param�tres
Extraire le fichier de configuration au format yaml utilis� pour initialiser l'extracteur de pyradiomics et l'envoyer � Thomas pour valider le choix des param�tres d'extractions. (e.g. le bin width doit �tre � 0.3)
- Choix du mod�le d'apprentissage
Les labels qui seront utilis�s dans l'apprentissage sont stock�s dans un tableur contenant le temps au bout duquel un patient a rechut�.
D'un point de vue clinique, une classification binaire "patient a rechut�" / "patient n'a pas rechut�" n'a pas de sens car les patients atteints de cette maladie rechutent dans la majeure partie des cas. Un mod�le de SVM binaire n'est pas pertinent.
Envisager l'approche random forest et lire le papier de 2008 RANDOM SURVIVAL FORESTS 1 By Hemant Ishwaran, Udaya B. Kogalur, Eugene H. Blackstone and Michael S. Lauer et se renseigner sur le code python existant.
--- Prochaines �tapes
�	R�cup�rer le jeu de donn�es au CHU aupr�s de Thomas (RDV jeudi 01/02 apr�s-midi, horaire � d�finir)
�	Impl�menter la standardisation des donn�es dans le pipe de pr�-traitement
�	Envoyer le fichier de configuration d'extraction de pyradiomics � Thomas
�	Valider les valeurs des features sur le sample des 3 patients 
�	Lire le papier random forest, rechercher un code Python �quivalent et designer un code python pouvant traiter des batchs de patients labelis�s (le label n�est pas pris en compte actuellement dans le pipe --> pourrait simplement �tre un attribut de la class Patient)

Les features � extraire pour comparer avec les donn�es de Thomas sont les suivantes :
- EntropyGLCM
- HomogeneityGLCM
- SUVmax
- SUVpeak
- Volume
- TLG
- NbVoxel
- DissimilarityGLCM
- HGRE
- ZLNU
- SZHGE
- ZP

---------------------------
### 5 f�vrier 2018
- instancier un extracteur depuis un fichier params.yaml
- regarder les features demand�es par Thomas et comparer les d�finitions math�matiques avec celles de pyradiomics.
- d�composer le code en une partie extraction de features et un partie machine learning
- d�composer le pipe en plusieurs scripts .py pour un code plus modulaire
- code pour convertir la pile de dcm en suv.

---------------------------
### R�union du 7 f�vrier 2018 avec Thomas
R�cup�ration des donn�es
- Faire attention aux masques d�j� construit 25.tif et 40.tif --> ils sont de la forme num�rique 0 et 255 (seulement les deux valeurs extr�mes) - en gros ils ne sont pas au format binaire - il faut les remettre en binaire pour �viter les probl�mes lors du calcul du masque par m�thode vote majoritaire.
---- Lexique du fichier csv dont on extrait les features par l�sion et par patient :
- endpointPFS ->  1 si patient a rechut�, 0 s�il ne rechute pas
- time to PFS : temps en jours au cours duquel le patient a rechut�. Pour les patients qui n'ont pas rechut�, cette date correspond aux derni�res nouvelles
Attention, pour faire la comparaison entre les valeurs de r�f�rence des features fournies par Thomas et celles calcul�es par pyradiomics, se baser sur le masque 40 uniquement.
Ne pas prendre en compte la feature TLG dans un premier temps. GLCM valid�.
Prendre ZP avec pr�caution (pas la m�me d�finition dans pyradiomics que celle adopt�e par Thomas dans son calcul de features).



--
### Note concernant la conversion des images Dicom et simple ITK
La fonction combine_slices de dicom_numpy applique le rescale slope / rescale intercept s�ils sont pr�sents dans les tags de l'image. Cf doc http://dicom-numpy.readthedocs.io/en/latest/index.html?highlight=combine%20slice
The image array dtype will be preserved, unless any of the DICOM images contain either the Rescale Slope or the Rescale Intercept attributes. If either of these attributes are present, they will be applied to each slice individually.
