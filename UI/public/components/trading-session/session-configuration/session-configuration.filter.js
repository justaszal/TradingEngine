export default function symbolsFilter(supportedCoins) {
  return arr => arr.filter(
    symbol => supportedCoins.coins.filter(
      coin => symbol.indexOf(coin) !== -1).length > 0);
}
