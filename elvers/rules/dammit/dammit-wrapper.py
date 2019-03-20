"""Snakemake wrapper for Dammit"""

__author__ = "Tessa Pierce"
__copyright__ = "Copyright 2018, Tessa Pierce"
__email__ = "ntpierce@gmail.com"
__license__ = "MIT"

from os import path
from snakemake.shell import shell

# handle database params
db_dir = snakemake.params.get("db_dir")
db_dir = path.abspath(db_dir)
busco_dbs = snakemake.params.get("busco_dbs", [])
db_extra = snakemake.params.get("db_extra", "")
db_only = snakemake.params.get('db_install_only', False)

if db_dir:
    db_dir = path.expanduser(db_dir)
    db_cmd = ' --database-dir ' + db_dir # if db_dir is not None else ""
else:
    db_cmd = ""

#db_cmd = ' --database-dir ' + db_dir if db_dir is not None else ""
log = snakemake.log_fmt_shell(stdout=False, stderr=True)

busco_dbs = [busco_dbs] if isinstance(busco_dbs, str) else busco_dbs
busco_cmd = ' --busco-group ' + ' --busco-group '.join(busco_dbs) if busco_dbs is not None else ""

# handle annotate params
outdir = path.dirname(snakemake.output[0])
annot_extra = snakemake.params.get("annot_extra", "")

# make informative output dir for *all* dammit output
assembly_name = path.basename(str(snakemake.input))
dammit_dir =  path.join(outdir, assembly_name + '.dammit')
dammit_fasta = path.join(dammit_dir, assembly_name + '.dammit.fasta')
dammit_gff3 = path.join(dammit_dir, assembly_name + '.dammit.fasta')

# run installation of everything *except* busco groups
shell("dammit databases --install {db_cmd} {db_extra} {log}") #--n_threads {snakemake.threads}

# busco groups need to be installed separately
for busco_grp in busco_dbs:
    shell("dammit databases --install {db_cmd} --busco-group {busco_grp} {db_extra} {log}") #--n_threads {snakemake.threads}

if not db_only:
# run annotation
    shell("dammit annotate {snakemake.input} {db_cmd} --n_threads {snakemake.threads} --output-dir {dammit_dir} {annot_extra} {log}")

# cp final dammit annot files to desired location / names
shell("cp {dammit_fasta} {snakemake.output.fasta}")
shell("cp {dammit_gff3} {snakemake.output.gff3}")

