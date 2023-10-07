load data local infile "/tmp/cleaned_data/covid19_timeseries.csv" 
into table covid19_timeseries 
fields terminated by "," 
enclosed by '"' 
lines terminated by "\n" 
ignore 1 rows;




load data local infile "/tmp/cleaned_data/worldometer.csv" 
into table worldometer 
fields terminated by "," 
enclosed by '"' 
lines terminated by "\n" 
ignore 1 rows;