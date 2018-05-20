export default function candlestickChartService() {
  const groupingUnitsDefault = [
    [
      // unit name
      'week',
      // allowed multiples
      [1],
    ],
    ['month', [1, 2, 3, 4, 6]],
  ];

  function createCandlestickChartConfiguration(title, groupingUnits = groupingUnitsDefault,
    rangeSelected = 5, split = true) {
    return {
      rangeSelector: {
        selected: rangeSelected,
      },
      title: {
        text: title,
      },
      tooltip: {
        split,
      },
      plotOptions: {
        series: {
          dataGrouping: {
            units: groupingUnits,
          },
        },
      },
      series: [],
    };
  }

  function setSubtitle(cfg, text) {
    return {
      ...cfg,
      subtitle: {
        text,
      },
    };
  }

  function setSeriesCandles(cfg, ohlc, name, params = {}) {
    // cfg.series = [];
    cfg.series.push({
      type: 'candlestick',
      name,
      data: ohlc,
      ...params,
    });

    return cfg;
  }

  function setSeriesVolume(cfg, volume) {
    cfg.series.push({
      type: 'column',
      name: 'Volume',
      id: 'volume',
      data: volume,
      yAxis: 1,
    });

    return cfg;
  }
  // zIndex
  function setSeriesEma(cfg, linkedTo, period = 14, params = {}) {
    return {
      ...cfg,
      linkedTo,
      period,
      ...params,
    };
  }

  /*
    rangeSelector: {
    buttons: [{
      type: 'hour',
      count: 1,
      text: '1h',
    }, {
      type: 'day',
      count: 1,
      text: '1D',
    }, {
      type: 'all',
      count: 1,
      text: 'All',
    }],
    selected: selected,
    inputEnabled: inputEnabled,
  */
  function setRangeSelectors(cfg, selected = 5, buttons = [], inputEnabled = false) {
    const o = {
      ...cfg,
      rangeSelector: {
        selected,
        inputEnabled,
      },
    };

    return buttons.length > 0 ? {
      ...o,
      buttons,
    } : o;
  }

  function setOhlcvYaxis(cfg) {
    return {
      ...cfg,
      yAxis: [{
        startOnTick: false,
        endOnTick: false,
        labels: {
          align: 'right',
          x: -3,
        },
        title: {
          text: 'OHLC',
        },
        height: '60%',
        lineWidth: 2,
        resize: {
          enabled: true,
        },
      }, {
        labels: {
          align: 'right',
          x: -3,
        },
        title: {
          text: 'Volume',
        },
        top: '65%',
        height: '35%',
        offset: 0,
        lineWidth: 2,
      }],
    };
  }

  function styleScrollbar(cfg) {
    return {
      ...cfg,
      scrollbar: {
        barBackgroundColor: 'gray',
        barBorderRadius: 7,
        barBorderWidth: 0,
        buttonBackgroundColor: 'gray',
        buttonBorderWidth: 0,
        buttonBorderRadius: 7,
        trackBackgroundColor: 'none',
        trackBorderWidth: 1,
        trackBorderRadius: 8,
        trackBorderColor: '#CCC',
      },
    };
  }

  return {
    createCandlestickChartConfiguration,
    styleScrollbar,
    setOhlcvYaxis,
    setRangeSelectors,
    setSeriesCandles,
    setSeriesVolume,
    setSeriesEma,
    setSubtitle,
  };
}
