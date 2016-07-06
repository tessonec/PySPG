== Example
The following is a sample session

=== Loading databases

[tessonec@lacar-vm:random-walk-py] 
[tessonec@lacar-vm:random-walk-py] spg-db.py init --repeat=10 simul1 
 **-- init       - 1: 'simul1.spgql'   
[tessonec@lacar-vm:random-walk-py] spg-db.py init --repeat=4 simul2 weight=5
 **-- init       - 2: 'simul2.spgql'   
[tessonec@lacar-vm:random-walk-py] spg-db.py ls
 --- registered dbs
    1: simul1.spgql (1.00000)
    2: simul2.spgql (5.00000)
 --- cwd matches found
     : simul1.spgql 
     : simul2.spgql 

=== Running databases single-thread
[tessonec@lacar-vm:random-walk-py] spg-run-standalone.py simul2
[spg-run-standalone.py -   MSG ] running simulation
^C
[spg-run-standalone.py -   SYS ] keyboard interrupted, exiting
[tessonec@lacar-vm:random-walk-py] spg-db.py info simul2
 ---    2: simul2.spgql
   -+ status = R /  weight: 1.00000 
   -+ total  = 42*4 / done: 52 (1.23810) - running: 0 - error: 0 
   -+ time   = 11.597820 / mean: 0.227408 - min: 0.079635 - max: 6.796639


=== Running databases multi-threaded

tessonec@lacar-vm:random-walk-py] spg-db.py get_jobs
 +--- no_jobs = 16 
[tessonec@lacar-vm:random-walk-py] spg-db.py set_jobs 5
[tessonec@lacar-vm:random-walk-py] spg-run-threaded.py 
[spg-run-threaded.py - STATUS ] [n_jobs=5] run=0 ::: new=5
-D- [   1]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 72
-D- [   2]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 73
-D- [   3]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 74
-D- [   4]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 75
-D- [   5]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 3
-X- [   1]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 72 -> 0
-X- [   2]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 73 -> 0
-X- [   3]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 74 -> 0
-X- [   4]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 75 -> 0
-X- [   5]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 3 -> 0
[spg-run-threaded.py - STATUS ] [n_jobs=5] run=0 ::: new=5
-D- [   6]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 76
-D- [   7]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 77
-D- [   8]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 78
-D- [   9]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 79
-D- [  10]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 4
-X- [   6]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 76 -> 0
-X- [   7]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 77 -> 0
-X- [   8]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 78 -> 0
-X- [   9]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 79 -> 0
-X- [  10]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 4 -> 0
[spg-run-threaded.py - STATUS ] [n_jobs=5] run=0 ::: new=5
-D- [  11]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 80
-D- [  12]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 5
-D- [  13]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 81
-D- [  14]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 82
-D- [  15]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 83
-X- [  11]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 80 -> 0
-X- [  12]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql / 5 -> 0
-X- [  13]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 81 -> 0
-X- [  14]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 82 -> 0
-X- [  15]- ----- /mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql / 83 -> 0

=== Registering/deregistering databases
Only registered databases run in a multithreaded environment

[tessonec@lacar-vm:random-walk-py] spg-db.py deregister 2
[tessonec@lacar-vm:random-walk-py] spg-db.py ls
 --- registered dbs
    1: simul1.spgql (1.00000)
 --- cwd matches found
     : simul1.spgql 
     : simul2.spgql

     : simul2.spgql 
[tessonec@lacar-vm:random-walk-py] spg-db.py deregister simul1


Databases can be referred to by name (with or without extension or number if they are registered)

== Saving data

[tessonec@lacar-vm:random-walk-py] spg-table.py help save_table
save_table [-flag1 -flag2] 
          saves the table values in ascii format. default is averaging column values by variable values
          FLAGS::: --noheader:    does not output column names in the output file
                   --raw:         raw  values without average
                   --full:        all simulation ids and variables are output in table (implies raw)
                   --id:          only the id is output
                   --sep:         column separator ('blank' for space)
       
[tessonec@lacar-vm:random-walk-py] spg-table.py save_table simul1
  +- table:  'simul1_results.csv'
[tessonec@lacar-vm:random-walk-py] head simul1_results.csv 
drift,Q,D,final_position,squared_displacement
0,0.1,0,0.0,0.0
0,0.1,0.5,3.81553297432,24.7090390741
0,0.1,1.0,-7.4951918649,110.588559438
0,0.1,1.5,-6.49728951738,168.094230062
[tessonec@lacar-vm:random-walk-py] spg-table.py save_table --full simul1
  +- table:  'simul1_results.csv'
[tessonec@lacar-vm:random-walk-py] head simul1_results.csv 
spg_uid,spg_vsid,spg_rep,drift,Q,D,final_position,squared_displacement
1,1,0,0,0.1,0,0.0,0.0
2,2,0,0,0.1,0.5,3.81553297432,24.7090390741
3,3,0,0,0.1,1.0,-7.4951918649,110.588559438
4,4,0,0,0.1,1.5,-6.49728951738,168.094230062
[tessonec@lacar-vm:random-walk-py] spg-table.py save_table --id simul1
  +- table:  'simul1_results.csv'
[tessonec@lacar-vm:random-walk-py] head simul1_results.csv 
spg_uid,final_position,squared_displacement
1,0.0,0.0
2,3.81553297432,24.7090390741
3,-7.4951918649,110.588559438
[tessonec@lacar-vm:random-walk-py] spg-table.py save_input_table simul1
 --- loaded: '/mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1.spgql'
  +- structure = [] - [] - [u'drift', u'Q', u'D'] 
  +- table:  '/mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul1_valueset.csv'
[tessonec@lacar-vm:random-walk-py] head simul1_valueset.csv 
spg_uid,simulation_timesteps,model,drift,Q,D
1,100,BIASED,0,0.1,0
2,100,BIASED,0,0.1,0.5

For simul2.spg there is an example of sting replacement

[tessonec@lacar-vm:random-walk-py] spg-table.py save_input_table simul2
 --- loaded: '/mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2.spgql'
  +- structure = [] - [] - [u'drift', u'D'] 
  +- table:  '/mnt/hgfs/tessonec/Development/PySPG/examples/random-walk-py/simul2_valueset.csv'
[tessonec@lacar-vm:random-walk-py] head simul2_valueset.csv 
spg_uid,simulation_timesteps,model,output_file,drift,D
1,100,BIASED,drift-0_D-0.0.net,0,0
2,100,BIASED,drift-0_D-0.5.0.net,0,0.5

