<?php
if(isset($_POST['submit']))
{
	if(isset($_POST['sysmode']))
        {
                $new_sysmode = $_POST['sysmode'];
                exec('/home/homecontrol/pyStat/setStat.py -m '.$new_sysmode, $output);
        }
	if(isset($_POST['setpoint']))
	{
		$new_setpoint = $_POST['setpoint'];
		exec('/home/homecontrol/pyStat/setStat.py -t '.$new_setpoint, $output);
	}
	if(isset($_POST['fanmode']))
	{
		$new_fanmode = $_POST['fanmode'];
		exec('/home/homecontrol/pyStat/setStat.py -f '.$new_fanmode, $output);
	}
	if(isset($_POST['schedmode']))
        {
                $new_schedmode = $_POST['schedmode'];
                exec('/home/homecontrol/pyStat/setStat.py -s '.$new_schedmode, $output);
        }
}
exec('/home/homecontrol/pyStat/getStat.py -b 2>&1', $output);
preg_match('/Temperature: (?P<value>\d+)/',$output[0],$matches);
$data['temp']=$matches['value'];
preg_match('/Set Point: (?P<value>\d+)/',$output[1],$matches);
$data['setpoint']=$matches['value'];
preg_match('/Mode: (?P<value>\w+)/',$output[2],$matches);
$data['mode']=$matches['value'];
preg_match('/Fan Mode: (?P<value>\w+)/',$output[3],$matches);
$data['fanmode']=$matches['value'];
preg_match('/Schedule Mode: (?P<value>\w+)/',$output[4],$matches);
$data['schedmode']=$matches['value'];
?>
<html>
<head>
<title>Thermostat Information</title>
</head>
<body>
<h1>Temperature: <?php echo $data['temp']; ?></h1>
<h1>Set Point: <?php echo $data['setpoint']; ?></h1>
<h1>Mode: <?php echo $data['mode']; ?></h1>
<h1>Fan Mode: <?php echo $data['fanmode']; ?></h1>
<h1>Schedule Mode: <?php echo $data['schedmode']; ?></h1>
<form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
New Set Point: <input type="text" name="setpoint"><br>
New System Mode: <input type="radio" name="sysmode" value="off"> Off <input type="radio" name="sysmode" value="heat"> Heat <input type="radio" name="sysmode" value="cool"> Cool<br>
New Fan Mode: <input type="radio" name="fanmode" value="on"> On <input type="radio" name="fanmode" value="auto"> Auto<br>
New Schedule Mode: <input type="radio" name="schedmode" value="run"> Run <input type="radio" name="schedmode" value="hold"> Hold<br>
<input type="submit" name="submit" value="Submit Form"><br>
</form>
</body>
</html>
