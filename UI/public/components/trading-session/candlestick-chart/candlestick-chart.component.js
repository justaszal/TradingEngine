import template from './candlestick-chart.html';
import style from './candlestick-chart.scss';


const candlestickChartComponent = {
  template,
  controller: class candlestickChart {
    constructor(tradingSessionService, candlestickChartService, $timeout) {
      this.tradingSessionService = tradingSessionService;
      this.candlestickChartService = candlestickChartService;
      this.$timeout = $timeout;
    }

    $onInit() {
      this.stockChartNames = [];
      this.baseChartName = 'candlestick-chart';

      this.tradingSessionService.startBacktestSession()
        .then((response) => {
          // console.log(response);
          const backtestReport = response.data;
          const candles = this.tradingSessionService.dataframeToCandlesAndVolumeArray(
            backtestReport.tickers_data);
          // console.log(candles['BTC/USDT']);

          Object.keys(candles).forEach((ticker, index) => {
            const candle = candles[ticker];

            let chartConfig = this.candlestickChartService.createCandlestickChartConfiguration(
              `${ticker} backtest result`,
            );
            chartConfig = this.candlestickChartService.setRangeSelectors(chartConfig);
            chartConfig = this.candlestickChartService.setOhlcvYaxis(chartConfig);
            chartConfig = this.candlestickChartService.setSeriesCandles(chartConfig,
              candle.ohlc, ticker);
            chartConfig = this.candlestickChartService.setSeriesVolume(chartConfig,
              candle.volume);
            chartConfig = this.candlestickChartService.styleScrollbar(chartConfig);

            const chartName = `${this.baseChartName}${index}`;
            this.stockChartNames.push(chartName);
            console.log(this.stockChartNames);
            console.log(chartName);

            this.$timeout(() => {
              Highcharts.stockChart(chartName, chartConfig);
            });
          });
          // console.log(chartConfig.series);
        });
      // // split the data set into ohlc and volume
      // let ohlc = [],
      //   volume = [],
      //   dataLength = data.length,
      //   // set the allowed units for data grouping
      //   groupingUnits = [[
      //     'week', // unit name
      //     [1], // allowed multiples
      //   ], [
      //     'month',
      //     [1, 2, 3, 4, 6],
      //   ]],
      //   // i = 0;

      // for (i; i < dataLength; i += 1) {
      //   ohlc.push([
      //     data[i][0], // the date
      //     data[i][1], // open
      //     data[i][2], // high
      //     data[i][3], // low
      //     data[i][4], // close
      //   ]);

      //   volume.push([
      //     data[i][0], // the date
      //     data[i][5], // the volume
      //   ]);
      // }



      //   rangeSelector: {
      //     selected: 5,
      //   },


      //   title: {
      //     text: 'AAPL Historical',
      //   },

      //   // subtitle: {
      //   //     text: 'With SMA and Volume by Price technical indicators',
      //   // },

      //   yAxis: [{
      //     startOnTick: false,
      //     endOnTick: false,
      //     labels: {
      //       align: 'right',
      //       x: -3,
      //     },
      //     title: {
      //       text: 'OHLC',
      //     },
      //     height: '60%',
      //     lineWidth: 2,
      //     resize: {
      //       enabled: true,
      //     },
      //   }, {
      //     labels: {
      //       align: 'right',
      //       x: -3,
      //     },
      //     title: {
      //       text: 'Volume',
      //     },
      //     top: '65%',
      //     height: '35%',
      //     offset: 0,
      //     lineWidth: 2,
      //   }],

      //   tooltip: {
      //     split: true,
      //   },

      //   plotOptions: {
      //     series: {
      //       dataGrouping: {
      //         units: groupingUnits,
      //       },
      //     },
      //   },

      //   series: [{
      //     type: 'candlestick',
      //     name: 'AAPL',
      //     id: 'aapl',
      //     zIndex: 2,
      //     data: ohlc,
      //   },
      //   {
      //     type: 'column',
      //     name: 'Volume',
      //     id: 'volume',
      //     data: volume,
      //     yAxis: 1,
      //   },
      //     // {
      //     //     type: 'vbp',
      //     //     linkedTo: 'aapl',
      //     //     params: {
      //     //         volumeSeriesID: 'volume'
      //     //     },
      //     //     dataLabels: {
      //     //         enabled: false
      //     //     },
      //     //     zoneLines: {
      //     //         enabled: false
      //     //     }
      //     // },
      //   {
      //     type: 'ema',
      //     linkedTo: 'aapl',
      //     period: 14,
      //     zIndex: 1,
      //     marker: {
      //       enabled: false,
      //     },
      //   },
      //   {
      //     type: 'flags',
      //     data: [{
      //       x: 1366848000000,
      //       title: 'B',
      //       text: 'Bought',
      //     },
      //     ],
      //     onSeries: 'aapl',
      //     shape: 'squarepin',
      //     width: 16,
      //   }],
      // });
    }
  },
};

export default candlestickChartComponent;
