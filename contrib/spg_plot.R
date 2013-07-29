rm(list=ls());gc();ls(); options(help_type = "html"); library("igraph");
source(paste('~/run/spg_plot_functions.R',sep=''))

##################################################################################
par(mfrow=c(4,4),mar=c(1,2.4,2,0.9),oma=c(4.5,2.2,2.5,2),mgp=c(1.7,0.5,0),cex=0.5)
##################################################################################


##### SELECTING FOLDER NAME #####
project <- "knowledge_exploration"
#project <- "onedimensional_knowledge"
#project <- "firms"
setwd(paste("~/run/",project,sep=""))

##### READING FROM OUTPUT FILE #####
#dat<-read.table(file=paste("/mnt/ethz/home/run/knowledge_exploration/output.dat",sep=""),header=TRUE)
dat<-read.table(file=paste(getwd(),"/output.dat",sep=""),header=TRUE)
names(dat)


# possible restriction(s) to data
unique(dat$mu)
unique(dat$N)
unique(dat$DIMENSIONS)
#dat <- dat[dat$lambda==1,]
#dat <- dat[dat$upp_threshold==0.3,]
#dat <- dat[dat$mu == 0.1,]
#dat <- dat[dat$N == 50,]
#dat <- dat[dat$DIMENSIONS == 3,]

x <- "lambda"
#y <- "know_path_mean"
y <- "convergence_time"
#y <- "cluster_number"
yLog <- T
parameter <- "upp_threshold"


#### MULTIPLE PLOTS ####
col_spec <- "DIMENSIONS"; col_values <- c(3,10)
#row_spec <- "N"; row_values <- c(200)
row_spec <- "mu"; row_values <- c(0.001,0.01,0.1,1)
par(mfrow=c(length(row_values),length(col_values)),mar=c(1.3,2.6,2.4,1),oma=c(2.5,1.5,1.5,1.5),mgp=c(1.7,0.5,0),cex=0.7)

for (rx in row_values) {
  for (cx in col_values) {
    mydata <- dat[(dat[,row_spec]==rx)&(dat[,col_spec]==cx),]
    plot_title <- paste(row_spec,"=",rx,", ",col_spec,"=",cx,sep="")
    xaxis <- ifelse (rx==row_values[length(row_values)],TRUE,FALSE)
    plot_results(mydata,x,y,parameter,plot_title,xaxis,ylog=yLog)
  }
}






####### PLOTS FOR ECCS ABSTRACT #########
par(mfrow=c(3,1),oma=c(3,0,0.3,0),mar=c(0,3.0,0,2.0))
y1 <- c("cluster_number","know_path_mean","convergence_time")
ylabel <- c("Clusters Number","Mean Knowledge Path","Convergence Time")
yLog <- c(T,F,T)
xaxis <- c(F,F,T)
maxy <- c(10,1.65,40000)
mylegend <- c(T,F,F)
mydata <- dat[(dat[,row_spec]==500)&(dat[,col_spec]==3),]
for (i in 1:3) {
  plot_results_for_abstract(mydata,x,y1[i],parameter,plot_title="",xaxis[i],ylog=yLog[i],ylabel[i],maxy[i],mylegend[i])
}











