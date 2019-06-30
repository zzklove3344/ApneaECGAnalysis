/* file: distill.c		G. Moody		12 April 2000

This program "distills" a set of annotation files for the CinC Challenge 2000
in one of two ways:

1. Using the -s option, it classifies the records as 'A' (containing at least
   100 minutes of detected apnea), 'B' (containing between 5 and 99 minutes of
   detected apnea), or 'C' (containing between 0 and 4 minutes of detected
   apnea).  In this case, the output contains one line for each record; each
   line contains the record name, followed by a space, followed by the
   classification ('A', 'B', or 'C').  The output obtained in this way for a
   set of annotation files for the training set (x01, x02, ..., x35) can be
   submitted to obtain a score for event 1 (apnea screening).

   Note that this is provided as a convenience only.  You may use any algorithm
   you wish to classify records for event 1 -- it is not necessary to follow
   the criteria described above, and it is not necessary even to have created
   a set of annotation files.  If you do not use this program to prepare your
   submission for event 1, download:
       http://www.physionet.org/physiobank/database/apnea-ecg/challenge/template-test-1
   and change the '?' characters to 'A', 'B', or 'C' as appropriate based on
   your classifications.  Submit the edited version of this template to obtain
   your scores.

2. If the -s option is omitted, it produces a condensed minute-by-minute
   account of each annotation file on the standard output.  For each record, it
   prints an empty line, followed by the record name on a line by itself, then
   prints a line of data for each hour in the record.  Each data line begins
   with an hour number and is followed by a space and 60 characters that
   indicate for each minute if apnea was detected ('A') or not ('N').  The
   output obtained in this way for a set of annotation files for the training
   set (x01, x02, ..., x35) can be submitted to obtain a score for event 2
   (quantitative assessment of apnea).

   Important:  The input annotation files should contain N (anntyp = 1) or A
   (anntyp = 8) annotations at one-minute (6000-sample) intervals, beginning at
   sample 0.  Any other annotations are ignored.  If neither an N nor an A
   annotation is found where one is expected, an 'X' is recorded in the output;
   this will be treated as an error when scores are calculated for event 2.

   Note that you do not need to use this program to enter event 2, either.  If
   you do not, download:
       http://www.physionet.org/physiobank/database/apnea-ecg/challenge/template-test-2
   and change the '?' characters to 'A' or 'N' as appropriate based on your
   classifications.  Submit the edited version of this template to obtain your
   scores.

Compile this program using the WFDB library (which may be downloaded from
http://www.physionet.org/physiotools/wfdb.shtml):
   cc -o distill distill.c -lwfdb

This program has been used to produce the summaries that can be downloaded
from http://www.physionet.org/physiobank/database/apnea-ecg/challenge/.   
Within that directory, summary-training-1 was produced using the command
   distill -a apn -s a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 \
           a11 a12 a13 a14 a15 a16 a17 a18 a19 a20 \
	   b01 b02 b03 b04 b05 \
           c01 c02 c03 c04 c05 c06 c07 c08 c09 c10 >summary-training-1
and summary-training-2 was produced using the command
   distill -a apn a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 \
           a11 a12 a13 a14 a15 a16 a17 a18 a19 a20 \
	   b01 b02 b03 b04 b05 \
           c01 c02 c03 c04 c05 c06 c07 c08 c09 c10 >summary-training-2

Similar files were produced for the test set (x01 ... x35);  these will be
posted after the conclusion of the competition in September.

The template files that can be found in the same directory were produced from
the summary files by translating all of the 'A', 'B', 'C', and 'N' characters
into '?' characters, using the UNIX 'tr' utility:
    tr ABCN \? <summary-training-1 >template-training-1
etc.

*/

#include <stdio.h>
#include <wfdb/wfdb.h>

/* The definitions below were chosen for convenience, because the mnemonic
   for a type 1 annotation is "N" and for a type 8 annotation is "A" (see
   <wfdb/ecgmap.h> for details if you're curious). */
#define NOAPNEA	1
#define APNEA	8

char *pname;
int sflag;
WFDB_Anninfo ai;

main(int argc, char **argv)
{
    int i;
    void distill(), help();

    pname = argv[0];

    if (argc < 4)
	help();

    /* Interpret command-line options. */
    for (i = 1; i < argc; i++) {
	if (*argv[i] == '-') switch (*(argv[i]+1)) {
	  case 'a':	/* annotator follows */
	    if (++i >= argc) {
		(void)fprintf(stderr, "%s: annotator must follow -a\n",
			      pname);
		exit(1);
	    }
	    ai.name = argv[i]; ai.stat = WFDB_READ;
	    break;
	  case 'h':	/* print help and quit */
	    help();
	    break;
	  case 's':	/* short mode */
	    sflag = 1;
	    break;
	  default:
	    (void)fprintf(stderr, "%s: unrecognized option %s\n",
			  pname, argv[i]);
	    exit(1);
	}
	else		/* argument must be a record name */
	    distill(argv[i]);
    }
    exit(0);
}

void help()
{
    fprintf(stderr, "Usage:\n"
	    "   %s -a ANNOTATOR [-s] RECORD1 [RECORD2 ...]\n"
	    "where ANNOTATOR is the annotator name (suffix) of the files"
	    " to be 'distilled'\n",
	    "and RECORD1, RECORD2, etc. are the record names for these"
	    " files.\n", pname);
    exit(1);
}

void distill(char *record)
{
    int apnea_minutes = 0, hours = -1, minutes = 60;
    WFDB_Annotation annot;
    WFDB_Time texpected = 0L;

    if (ai.name == NULL)
	help();

    printf("%s", record);
    if (annopen(record, &ai, 1) < 0) {
	printf(" [no annotations]\n");
	return;
    }

    while (getann(0, &annot) == 0) {
	if (annot.time < texpected) continue;	/* ignore extra annotations */
	while (texpected < annot.time) { /* fill in for missing annotations */
	    texpected += 6000L;	/* one minute at 100 samples/second */
	    if (!sflag) {
		if (++minutes >= 60) {
		    printf("\n%2d ", ++hours);
		    minutes = 0;
		}
		printf("X");
	    }
	}
	if (annot.time == texpected) {	/* a valid annotation -- record it */
	    texpected += 6000L;	/* one minute at 100 samples/second */
	    if (!sflag) {
		if (++minutes >= 60) {
		    printf("\n%2d ", ++hours);
		    minutes = 0;
		}
		if (annot.anntyp == NOAPNEA)
		    printf("N");
		else if (annot.anntyp == APNEA)
		    printf("A");
		else
		    printf("X");
	    }
	    else if (annot.anntyp == APNEA)
		apnea_minutes++;
	}
    }
    if (sflag) {	/* classify the record */
	if (apnea_minutes >= 100) printf(" A");
	else if (apnea_minutes >= 5) printf(" B");
	else printf(" C");
    }
    printf("\n");
    if (!sflag) printf("\n");
}
