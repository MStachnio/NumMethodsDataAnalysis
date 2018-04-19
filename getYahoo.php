<?
# Example code
# peter.gruber@usi.ch

# get data from google finance and write it into the database
$url1='https://query.yahooapis.com/v1/public/yql?q=';
$url2='select symbol,PreviousClose,Open,DaysLow,DaysHigh,LastTradePriceOnly,LastTradeTime,LastTradeDate,Volume from yahoo.finance.quotes where symbol in ("^VIX","^VIXMO","^VIXJAN","^VIXFEB","^VIXMAR","^VIXAPR","^VIXMAY","^VIXJUN","^VIXJUL","^VIXAUG","^VIXSEP","^VIXOCT","^VIXNOV","^VIXDEC","^GSPC","EURCHF=X","EURUSD=X","VXX","VIXY","VXZ","VIXM","XVIX","VIIX","UVXY","TVIX","TVIZ","XIV","ZIV","SVXY","^VXFXI")';
$url3='&format=json&env=store://datatables.org/alltableswithkeys';

# Example 
# $url='select symbol,PreviousClose,Open,DaysLow,DaysHigh,LastTradePriceOnly,LastTradeTime from yahoo.finance.quotes where symbol in ("^VIX","^VIXJAN","^VIXFEB")';

#echo $url1.urlencode($url2).$url3;
#echo "\n";
# pwd	google4Options!
# Databasename :	xxx
# Hostname   :	xxx.db.1and1.com
# Port       :	3306
# Username   :	xxx
# Version    :	MySQL5

$link = mysqli_connect("server", "user", "pwd", "db");
mysqli_error($link); 

require_once 'JSON.php';
$json = file_get_contents($url1.urlencode($url2).$url3);
$jsonService = new Services_JSON();
$allFutures=$jsonService->decode($json);
#var_dump($allFutures->query->results->quote);
$query = "INSERT INTO yahoo (timestamp, ticker, price, open, daysLow, daysHigh, previousClose, volume) VALUES (?,?,?,?,?,?,?,?)";
$statement = mysqli_prepare($link, $query);
$foo=$allFutures->query->results->quote;
mysqli_stmt_bind_param($statement, "ssssssss", $v1, $v2, $v3, $v4, $v5, $v6, $v7, $v8);
foreach ($foo as $myF)
		{
		$v1=date('Y-m-d',strtotime($myF->LastTradeDate)).' '.date('H:i:s',strtotime($myF->LastTradeTime));
		$v2=$myF->symbol;		$v3=$myF->LastTradePriceOnly;		$v4=$myF->Open;		
		$v5=$myF->DaysLow;		$v6=$myF->DaysHigh;					$v7=$myF->PreviousClose;
		$v8=$myF->Volume;
		# echo sprintf('%12s %8s %7.2f %7.2f %7.2f %7.2f %7.2f %9u',$v1, $v2, $v3, $v4, $v5, $v6, $v7, $v8);
		# echo "\n";
		mysqli_stmt_execute($statement);
		}
mysqli_close($link);
?>