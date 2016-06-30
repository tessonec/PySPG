
plot_results <- function(dat,x,y,parameter,plot_title,xaxis=TRUE,ylog,ylabel=y,maxy=max(dat_restr[,y])) {
  dat_restr <- dat #to be modified if further restrictions are required
  
  #### to display every value of the parameter ####
  vector_param <- unique(dat_restr[,parameter])
  #### to display customized values of the parameter ####
  #vector_param <- c(0,0.1,0.15,0.2,0.5,1)

  palette(rainbow(length(vector_param)))
  plot(c(min(dat_restr[,x]),50*max(dat_restr[,x])),c(min(dat_restr[,y]),maxy),log=ifelse(ylog,"xy","x"),
       xlab="",xaxt="n",ylab=ylabel,col="white",main=plot_title)
  if (xaxis==TRUE) {
    axis(1,at=c(0.00001,0.0001,0.001,0.01,0.1,1,10,100,1000,10000),labels=TRUE)
    mtext(expression(lambda),1,line=1.7,cex=0.8)
  }
  else 
    axis(1,at=c(0.00001,0.0001,0.001,0.01,0.1,1,10,100,1000,10000),labels=FALSE)

  for (i in 1:length(vector_param)) {
    dat_plot <- dat_restr[dat_restr[,parameter]==vector_param[i],]
    x_points <- dat_plot[,x]
    y_points <- dat_plot[,y]
    if(ylog==T) y_points <- dat_plot[,y]+1
    points(x_points,y_points,pch=19,col=i)
    lines(x_points,y_points,col=i)
  }

  mylegendtext <- NULL
  for (i in 1:length(vector_param)) {
    myvalue <- bquote(epsilon==.(vector_param[i]))
    mylegendtext[i] <- as.expression(substitute(x,list(x=myvalue)))
  }

  ##### code for legend text
  epsilon=c(2,3,4,5)
  fff=NULL
  for (i in 1:4) {
    e=epsilon[i]
    f=bquote(mu==.(e))
    fff=c(fff,as.expression(substitute(x,list(x=f))))
  }

  legend (legend=mylegendtext,col=palette(),pch=19,x="topright",bty="n",cex=0.85,y.intersp=1)

}




plot_results_for_abstract <- function(dat,x,y,parameter,plot_title,xaxis=TRUE,ylog,ylabel=y,maxy=max(dat_restr[,y]),print_legend=TRUE) {
  dat_restr <- dat #to be modified if further restrictions are required
  
  #### to display every value of the parameter ####
  #vector_param <- unique(dat_restr[,parameter])
  #### to display customized values of the parameter ####
  vector_param <- c(0,0.1,0.15,0.2,0.3,0.5)
  
  palette(rainbow(length(vector_param)))
  mysymbols <- c(0:(length(vector_param)-1))
  
  plot(c(min(dat_restr[,x]),2.7),c(min(dat_restr[,y]),maxy),log=ifelse(ylog,"xy","x"),
       xlab="",xaxt="n",ylab=ylabel,col="white",main=plot_title)
  if (xaxis==TRUE) {
    axis(1,at=c(0.00001,0.0001,0.001,0.01,0.1,1),labels=c("0.00001","0.0001",0.001,0.01,0.1,1))
    mtext(expression(lambda),1,line=1.7,cex=0.8)
  }
  else 
    axis(1,at=c(0.00001,0.0001,0.001,0.01,0.1,1),labels=FALSE)
  
  for (i in 1:length(vector_param)) {
    dat_plot <- dat_restr[dat_restr[,parameter]==vector_param[i],]
    x_points <- dat_plot[,x]
    y_points <- dat_plot[,y]
    ###below, set col=i to have colors from the customized palette
    ### and pch=mysymbols[i] to have customized plot symbols
    points(x_points,y_points,pch=mysymbols[i],col="black",cex=1.4)
    lines(x_points,y_points,col="black",lwd=0.5)
  }
  
  mylegendtext <- NULL
  for (i in 1:length(vector_param)) {
    myvalue <- bquote(epsilon==.(vector_param[i]))
    mylegendtext[i] <- as.expression(substitute(x,list(x=myvalue)))
  }
  
  ##### code for legend text
  epsilon=c(2,3,4,5)
  fff=NULL
  for (i in 1:4) {
    e=epsilon[i]
    f=bquote(mu==.(e))
    fff=c(fff,as.expression(substitute(x,list(x=f))))
  }
  
  #below, set col=palette() and/or pch=mysymbols to have customized colors and/or symbols
  if (print_legend==TRUE)
    legend (legend=mylegendtext,col="black",pch=mysymbols,x="topleft",bty="o",cex=0.9,y.intersp=1.2)
  
}


