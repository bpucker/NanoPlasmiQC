### Boas Pucker ###
### pucker@uni-bonn.de ###

__version__ = "v0.1.2"

__usage__ = """
			python3 clean_plasmid_seq_input.py
			--in <INPUT_FOLDER>
			--fasta <CLEAN_FASTA_FILE>
			--doc <DOCUMENTATION_FILE>
			"""

import glob, os, sys

# --- end of imports --- #

def main( arguments ):
	"""! @brief run everything """
	
	input_folder = arguments[ arguments.index('--in')+1 ]
	clean_FASTA_file = arguments[ arguments.index('--fasta')+1 ]
	doc_file = arguments[ arguments.index('--doc')+1 ]

	seq_len_cutoff = 50000	#50kb
	appendix = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"	#used for renaming multiple FASTA seqs
	extensions = [ "fasta", "fas", "fa", "FASTA", "FAS", "FA" ]

	if input_folder[-1] != "/":
		input_folder += "/"


	fasta_files = []
	for each in extensions:
		fasta_files += glob.glob( input_folder + "*." + each )

	print( "Number of files: " + str( len( fasta_files ) ) )

	name_mapping_table = {}	#store original names of renamed sequences

	# --- write all clean sequences into new FASTA file --- #
	with open( clean_FASTA_file, "w" ) as out:
		
		# --- reading FASTA files --- #
		for filename in fasta_files:
			
			# --- load data from FASTA file --- #
			ID = ".".join( filename.split('/')[-1].split('.')[:-1] )
			new_ID = []
			for each in ID:
				if each in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_":	#excludes all special characters
					new_ID.append( each )
				else:
					new_ID.append( "_" )
			ID = "".join( new_ID ) + ""
			ID = ID.replace( "__", "_" ).replace( "__", "_" )
			if ID[-1] == "_":
				ID = ID[:-1]
			#print( ID )
			seqs = {}
			with open( filename, "r" ) as f:
				header = f.readline().strip()[1:]	#read first header
				line = f.readline()
				seq = []
				while line:
					if line[0] == ">":
						seqs.update( { header: "".join( seq ) } )
						header = line.strip()[1:]
						seq = []
					else:
						seq.append( line.strip() )
					line = f.readline()
				seqs.update( { header: "".join( seq ) } )
			
			# --- check for multiple sequences in a file -> rename by adding a,b,c,d,... --- #
			if len( list( seqs.keys() ) ) == 1:	#each FASTA file should only contain one sequence
				key = list( seqs.keys() )[0]
				out.write( '>' + ID + "\n" + seqs[ key ] + "\n" )
				if len( seqs[ key ] ) > seq_len_cutoff:	#warning for large sequences >50kb
					print( "WARNING: sequence length exceeds cutoff (" + str( seq_len_cutoff ) + ") - " + key )
				name_mapping_table.update( { ID: key } )
			else:	#multiple sequences in one file
				print( "WARNING: multiple sequences in " + ID )
				for idx, key in enumerate( list( seqs.keys() ) ):
					out.write( '>' + ID + appendix[ idx ] + "\n" + seqs[ key ] + "\n" )
					if len( seqs[ key ] ) > seq_len_cutoff:	#warning for large sequences >50kb
						print( "WARNING: sequence length exceeds cutoff (" + str( seq_len_cutoff ) + ") - " + key )
					name_mapping_table.update( { ID + appendix[ idx ]: key } )

	# --- generate mapping table of renamed sequences --- #
	with open( doc_file, "w" ) as out:
		for key in sorted( list( name_mapping_table.keys() ) ):
			out.write( key + "\t" + name_mapping_table[ key ] + "\n" )


if '--in' in sys.argv and '--fasta' in sys.argv and '--doc' in sys.argv:
	main( sys.argv )
else:
	sys.exit( __usage__ )
