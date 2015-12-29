

<?php

// PTC - this is the webservice side of the Style Cleanup app

// when it's called, we need to:
//	 a) pull the data out of the POST
//	 b) see if it makes any sense
//	 c) connect to the database
//	 d) update the database
// 	 e) let the app know it worked (?)


// PTC - hurl.it was invaluable for testing

// Helper method to get a string description for an HTTP status code
// From http://www.gen-x-design.com/archives/create-a-rest-api-with-php/ 
function getStatusCodeMessage($status)
{
    // these could be stored in a .ini file and loaded
    // via parse_ini_file()... however, this will suffice
    // for an example
    $codes = Array(
        100 => 'Continue',
        101 => 'Switching Protocols',
        200 => 'OK',
        201 => 'Created',
        202 => 'Accepted',
        203 => 'Non-Authoritative Information',
        204 => 'No Content',
        205 => 'Reset Content',
        206 => 'Partial Content',
        300 => 'Multiple Choices',
        301 => 'Moved Permanently',
        302 => 'Found',
        303 => 'See Other',
        304 => 'Not Modified',
        305 => 'Use Proxy',
        306 => '(Unused)',
        307 => 'Temporary Redirect',
        400 => 'Bad Request',
        401 => 'Unauthorized',
        402 => 'Payment Required',
        403 => 'Forbidden',
        404 => 'Not Found',
        405 => 'Method Not Allowed',
        406 => 'Not Acceptable',
        407 => 'Proxy Authentication Required',
        408 => 'Request Timeout',
        409 => 'Conflict',
        410 => 'Gone',
        411 => 'Length Required',
        412 => 'Precondition Failed',
        413 => 'Request Entity Too Large',
        414 => 'Request-URI Too Long',
        415 => 'Unsupported Media Type',
        416 => 'Requested Range Not Satisfiable',
        417 => 'Expectation Failed',
        500 => 'Internal Server Error',
        501 => 'Not Implemented',
        502 => 'Bad Gateway',
        503 => 'Service Unavailable',
        504 => 'Gateway Timeout',
        505 => 'HTTP Version Not Supported'
    );
 
    return (isset($codes[$status])) ? $codes[$status] : '';
}
 


// Helper method to send an HTTP response code/message
function sendResponse($status = 200, $body = '', $content_type = 'text/html')
{
	$status_header = 'HTTP/1.1 ' . $status . ' ' . getStatusCodeMessage($status);
	header($status_header);
	header('Content-type: ' . $content_type);
	echo $body;
}



class UpdateDB	{

private $db;	
	// create DB connection when the object is created
	function __construct() {
		// mysqli (server, username, password, database)
		$this->db = new mysqli('localhost','petecart_1','Summer08','petecart_styleweekly');
		$this->db->autocommit(FALSE);
		echo 'Connection seems to have gone ok in the update';
	}

	// close DB connection when the object dies
	function __destruct(){
		$this->db->close();
	}

	// Update the DB with the new info
	function update(){
		error_log("Update is called");
		$postedData = json_decode($_POST["json"], TRUE);
		error_log(gettype($postedData));
		// confirm that we have at least the category name and one value to update
		// Do I need this?  Can I just ensure in the app that I never post anything but all of them
		if(!empty($postedData["category"])){
			error_log("Category is set, in the main if",0);
			// All we"re getting is the company name, the address, 
			// the places (2nd and 3rd will be blank usually), and the address if available
			$category = $postedData["category"];
			error_log($category);
			$first_place = $postedData["first_place"];
			error_log($first_place);
			$second_place = $postedData["second_place"];
			error_log($second_place);
			$third_place = $postedData["third_place"];
			error_log($third_place);
			$address = $postedData["address"];
			error_log($address);
			$phone = $postedData["phone"];
			error_log($phone);
			$url = $postedData["url"];
			error_log($url);

			// If this was a real thing, I would check for existing values and coalesce, BUT
			// since I want to get this done, I`m going to just assume we want to overwrite the uploaded values
			
			
			
			if (! $stmt = $this->db->prepare("UPDATE styleweekly_fix SET first_place=? , second_place=? , third_place=? , address=?, phone=?, url=?, fixed_flag = 'Y' WHERE category=?")) {
				error_log('DATA BASE Error: ' . $db->error,0);

			} else {
				error_log('Prepare went OK',0);
				/// sssssss = 7 strings
				$stmt->bind_param("sssssss", $first_place, $second_place, $third_place, $address, $phone, $url, $category);
				$stmt->execute();
				$this->db->commit();
				error_log($db->error);
			}

			// would not be a bad idea to reprocess the addresses here through google to get lat/long if possible

			// response 200 = OK
			//sendResponse(200,'looks like it worked','text/html');
		}
	}
}

class GetRecords {

	private $db;

	// create a DB connection when the object is created

	function __construct(){
		$this->db = new mysqli('localhost','petecart_1','Summer08','petecart_styleweekly');
		$this->db->autocommit(FALSE);

		// check connection
		if ($this->db->connect_error) {
		  trigger_error('Database connection failed: '  . $this->db->connect_error, E_USER_ERROR);
		}


	}

	// close it when we lose the object
	function __destruct(){
		$this->db->close();
	}

	function getRecords(){
		//if (isset($_GET['get_stuff'])) {
			$myQuery = "SELECT * from styleweekly_fix where fixed_flag = 'Y'";
			$stmt = $this->db->prepare($myQuery);
			$stmt->bind_result($id, $category, $first_place, $second_place, $third_place, $description, $address, 
								$address_lat, $address_long, $address_formatted, $url, $phone, $whose_pick, $style_url, $year, $fixed_flag );
			$stmt->execute();

			error_log('Pulled Promos',0);
			$to_json = array();
			while($stmt->fetch()){
				// put the data into the array
				$row = array('category'     	  => $category,
						  'first_place'  	  => $first_place,
						  'second_place'      => $second_place,
						  'third_place'       => $third_place,
						  'description'       => $description,
						  'address'           => $address,
						  'address_lat'       => $address_lat,
						  'address_long'      => $address_long,
						  'address_formatted' => $address_formatted,
						  'url'               => $url,
						  'phone'			  => $phone,
						  'whose_pick'        => $whose_pick,
						  'style_url'         => $style_url,
						  'year' 			  => $year,
						  'fixed_flag'        => $fixed_flag
						);
				$to_json[] = $row;
			}

			echo json_encode($to_json);


		//			$result = $this->db->query($myQuery) or die($this->db->error);
		//	echo $result->num_rows;
		//	while ($row = $result->fetch_assoc()){
		//		echo "checking rows";
		//		echo $json_encode($row)." , ";
		//	}

			// return the data to the app to handle
			//sendResponse('200',$json,'application/json');
	//	} else {
	//		echo "didn't ask for stuff!";
	//	}
	}
}




// if it's a POST, update the database

// if it's a GET, pull all the data that needs to get updated out of the database

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
	error_log('Request method is Post');
	$api = new UpdateDB;
	$api->update();
} else if ($_SERVER['REQUEST_METHOD'] === 'GET') {

	error_log('Request method is GET');
	$api = new GetRecords;
	$api->getRecords();
}




?>