<?php
function formToJson($formpost) {
	$sched = array();
	foreach ($formpost as $postkey => $value) {
		if(preg_match('/day([1-7])_period([1-4])_(.*)/', $postkey, $matches)) {
			if($matches[3]=="schedTime") {
				$sched['day'.$matches[1].'_period'.$matches[2]][$matches[3]]=$value;
			}
			else {
				$sched['day'.$matches[1].'_period'.$matches[2]][$matches[3]]=intval($value);
			}
			$sched['day'.$matches[1].'_period'.$matches[2]]['rcs_day_number']=intval($matches[1]);
			$sched['day'.$matches[1].'_period'.$matches[2]]['rcs_period_number']=intval($matches[2]);
		}
	}
	return json_encode($sched, JSON_PRETTY_PRINT);	
}
if(isset($_POST['formaction'])) {
	if($_POST['formaction']=="download") {
		header('Content-type: application/octet-stream');
		header('Content-Disposition: attachment; filename="Schedule.txt"');
		echo formToJson($_POST);
	}
	if($_POST['formaction']=="send") {
		$process=proc_open('/home/homecontrol/pyStat/schedStat.py -i', array( 0=> array("pipe", "r")), $pipes);
		if (is_resource($process)) {
			fwrite($pipes[0],formToJson($_POST));
			fclose($pipes[0]);
		}
		proc_close($process);
	}
}
else {
	exec('/home/homecontrol/pyStat/schedStat.py -o 2>&1', $output);
	echo implode("\n", $output);
}
?>