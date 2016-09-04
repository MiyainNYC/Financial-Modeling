f = decompose(AirPassengers)

f$figure

plot(f$figure, type = 'b',xaxt = 'n',xlab = '')

monthNames = months(ISOdate(2011,1:12,1))
axis(1,at = 1:12,labels = monthNames, las = 2)
plot(f)

#ARIMA

fit = arima(AirPassengers,order = c(1,0,0),list(order = c(2,1,0),period = 12))

fore = predict(fit,n.ahead = 24)

U = fore$pred + 2*fore$se
L = fore$pred -2*fore$se

ts.plot(AirPassengers, fore$pred, U, L, col=c(1,2,4,4), lty = c(1,1,2,2))

