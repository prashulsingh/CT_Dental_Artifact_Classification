
$(document).ready(function() {

    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

});
var i =0;
var info=[];
var csvFilesFound = [];
checkInIds=[];
reviewIds=[];
function showDicomFiles(context)
{
    var filesList = document.getElementById( 'client-files' ).files;
  
    if( Array.from(filesList).length == 0 )
        return;
    csvFilesFound = []
    checkInIds=[]
    reviewIds =[]
    i = 0;
    // retrieve files from the input type=file 
        //empty all the files within the image container
    document.getElementById("imagesContainer").innerHTML = "";
    // Add our tool, and set it's mode
    cornerstoneWADOImageLoader.wadouri.fileManager.purge();
    cornerstoneWADOImageLoader.wadouri.dataSetCacheManager.purge();

    Array.from(info).forEach( function( elementInfo ){
        cornerstone.disable( elementInfo[0] );
    });
    info=[];
  
    Array.from(filesList).forEach( function( file ){
        fileName = file.name;
        if( validFile( file ) )
        {
            document.getElementById("imagesContainer").insertAdjacentHTML('beforeend',  generateHTMLContentForImage(filesList[i]) );         
            element  = $("div[id='" + fileName + "_img_holder']").get(0);
            fileNameElement  = $("div[id='" + fileName + "_img_name']").get(0);
            fileNameElement.innerHTML = fileName;
            cornerstone.enable(element);
            imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
            info[i] = new Array(2);
            info[i][0] =  element;
            info[i][1] = imageId;
            i++;
            var context = this;     
        }
        else if ( fileName.endsWith( ".csv" ) )
        {
            csvFilesFound.push( file );
            
        }

    });

   csvFilesFound.sort((a, b) => (a.lastModified - b.lastModified))

    // console.log( csvFilesFound )

    Array.from(info).forEach( function( info ) {
    var element = cornerstone.loadImage(info[1]).then(function(image) {
        cornerstone.displayImage(info[0], image);
        cornerstoneTools.mouseInput.enable(info[0]);
        cornerstoneTools.mouseWheelInput.enable(info[0]);
        cornerstoneTools.wwwc.activate(info[0], 1); // ww/wc is the default tool for left mouse button
        cornerstoneTools.pan.activate(info[0], 2); // pan is the default tool for middle mouse button
        cornerstoneTools.zoom.activate(info[0], 4); // zoom is the default tool for right mouse button
        cornerstoneTools.zoomWheel.activate(info[0]); // zoom is the default tool for middle mouse wheel

    });
    });
    
    
    updateAnnotationFileFound();
    attachRadioButtonEvent();
}
function loadPrimaryRaterAnnotation()
{
    // console.log( "primaryAnnotation")
    
    let reader = new FileReader();
    let file = csvFilesFound[0];
    reader.readAsText(file);
    // console.log( file )
    reader.onload = function() {
        csvContent = reader.result;
        var lines = csvContent.split("\n");
        while( typeof lines[0] !== "undefined" ){
            var line = lines.shift();
            var split = line.split(',');
            var filePath = split[0];
            if( split.length <= 1 )
                continue;
            var categoryName = split[1].trim();
            var filename = filePath.replace(/^.*[\\\/]/, '');
            input = document.getElementsByName( filename );
            var event = new CustomEvent('change');

            if( "medium".localeCompare(categoryName) == 0 )
            {
                input[1].checked = true;  
                input[1].dispatchEvent(event);
            }  
            else if( "high".localeCompare(categoryName) == 0 )
            {
                input[2].checked = true;
                input[2].dispatchEvent(event);
            }
            else if( "excluded".localeCompare(categoryName) == 0 )
            {
                var event = new CustomEvent('click');
                input = document.getElementById(filename+"_exclude");
                input.checked = true;
                input.dispatchEvent(event);
            }
            
            
        }
    loadSecondaryRaterAnnotation();  
    };

    reader.onerror = function() {
        alert(reader.error);
    };
    
}
function getPrimaryRaterValue(filename)
{
    input = document.getElementsByName( filename );
    var excludedCheckBox = document.getElementById( filename + "_exclude" );
    if( excludedCheckBox.checked )
        return "excluded";
    for(i = 0; i < input.length; i++) { 
        if(input[i].checked) 
                return input[i].value; 

    }
return "";
}
function loadSecondaryRaterAnnotation()
{
    // console.log("Secondary Annotation");
    let reader = new FileReader();
    let file = csvFilesFound[1];
    // console.log( file );
    reader.readAsText(file);
    
    reader.onload = function() {
        csvContent = reader.result;
        var lines = csvContent.split("\n");
        while( typeof lines[0] !== "undefined" ){
            var line = lines.shift();
            var split = line.split(',');
            var filePath = split[0];
            var secondaryRatercategoryName = split[1].trim();
            var filename = filePath.replace(/^.*[\\\/]/, '');
            primaryRaterCategoryName = getPrimaryRaterValue( filename );

            if( primaryRaterCategoryName.localeCompare(secondaryRatercategoryName) != 0 )
            {
                var label = document.getElementById( filename + "_secondary_rater" );
                label.parentElement.parentElement.parentElement.classList.add("borderBlink");
                label.innerHTML ="Category Diff :" + secondaryRatercategoryName ;
                label.style.display="";
            }  
         

        }
    };

    reader.onerror = function() {
        alert(reader.error);
    };
}

function retrieveAnnotationFromCSV(){
    if( csvFilesFound == null || csvFilesFound.length < 2 )
        return;

    loadPrimaryRaterAnnotation();


}
function updateAnnotationFileFound()
{
    annotationLabel = document.getElementById( "annotationLabel"  );
    annotationFiles = document.getElementById( "annotationFiles"  );
    if( csvFilesFound.length ==  0 )
    {
        annotationLabel.style.display = "none";
        annotationFiles.style.display = "none";
    
    return;
    }
    annotationLabel.style.display = "inline";
    annotationFiles.style.display = "inline";
    csvFileList = []
    csvFilesFound.forEach(function(entry) {
        csvFileList.push(entry.name)
    });
    annotationFiles.innerHTML = csvFileList.toString();
    
}
function attachRadioButtonEvent()
{
    $('input[type=radio]').on('change', function() {
        switch ($(this).val()) {
        case 'low':
        $(this).parent().parent()[0].style.borderColor="white";
          break;
        case 'medium':
        $(this).parent().parent()[0].style.borderColor="blue";
          break;
        case 'high':
        $(this).parent().parent()[0].style.borderColor="red";
        break;
        }

    // Listen for the change event on our input element so we can get the
    // file selected by the user
    });
}

function generateHTMLContentForImage( fileInfo )
{
    var fileName = fileInfo.name;
    var htmlString = [ '<div class = "image" >',
    '<div id=\"' + fileName + "_img_holder" + '\" style="width:99%;height:90%;top:0px;left:0px; position:absolute">',
    '</div>',
    '<div id=\"' + fileName + "_img_name" + '\" style="position:absolute;top:0px;left:0px;color:white">',
    '</div>',
    '<div style="top:330px;width:100%; position:absolute; display:inline;color:black;margin:0px;">',
    '<input  checked type="radio"  name=\"' + fileName + '\" value="low" />',
        '<label for="one">Low</label>',
        '<input  type="radio" style="margin-left:25%" name=\"' + fileName + '\" value="medium" />',
        '<label >Medium</label>',
        '<input onchange="myFunction()" type="radio"  style=\"margin-left:9%\"name=\"' + fileName + '\" value="high" />',
        '<label >High</label>',
        '<div style=\"border-style: ridge\">',
        '<input type=\"checkbox\" id=\"' + fileName + "_review" + '\"  onclick=\"checkBoxReviewClick(this)\">',    
        '<label >Review</label>',
        '<input type=\"checkbox\" style=\"margin-left: 10%;\" type=\"checkbox\" id=\"' + fileName + "_exclude" + '\"  onclick=\"checkBoxExcludeClick(this)\">', 
        '<label >Exclude</label>',
        '<label style=\"margin-left: 4%;display:none\" id=\"' + fileName + "_secondary_rater" + '\"></label>',
        '</div>',
    '</div>',
'</div >' 
].join("\n");

    return htmlString;

}

function validFile( fileInfo  )
{
    return fileInfo.name.endsWith( ".dcm" );
}

function getParentDirectory(){
    var folderPath = document.getElementById( 'folder_loc' ).value;

    if( typeof(folderPath) == 'undefined' || folderPath === null || folderPath == ""   )
        alert( 'Please provide valid  folder path containig DICOM Images ');
    return folderPath;
}

// Get the modal
var modal = document.getElementById("retrieveAnnotation");

// Get the button that opens the modal
var btn = document.getElementById("retrieveAnnotationBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
function retrieveAnnotation()
{   
  modal.style.display = "block";
  document.getElementById( "folderLoc"  ).value = document.getElementById( "folder_loc"  ).value;
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href',  "data:text/csv;charset=utf-8," + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

// Start file download.
document.getElementById("download").addEventListener("click", function(){
    var folderPath = document.getElementById("folderLoc").value;
    if( folderPath.length == 0 || folderPath == "" )
    {
        alert("Please provide Folder name");
        return;
    }
    var csvContent = getContent( folderPath );
    var fileName = document.getElementById("annotationFileName").value;
    if( fileName.length == 0 ||  fileName == "" )
        {
                alert("Please provide annotation File Name");
                return;
        }
    download(fileName, csvContent);
    document.getElementById("retrieveAnnotation").style.display="none";
}, false);

function getContent( folderPath )
{
    radioBoxes = $('input[type=radio]:checked');
    content  = "";
	start = false;
    Array.from(radioBoxes).forEach( function( radioBox ){
        fileName = radioBox.name.substr( 0, radioBox.name.lastIndexOf("." ) );
        
        if( checkInIds.length >=2 && fileName == checkInIds[0] )
            start = true;

        if( start )
            row = folderPath + "\\" + radioBox.name + "," + "excluded" + "\r\n";    
        else
            row = folderPath + "\\" + radioBox.name + "," + radioBox.value + "\r\n";

        if( checkInIds.length >=2 && fileName == checkInIds[checkInIds.length-1] )
            start = false;

        content = content + row;
    });
    return content;
}

window.onscroll = function() {myFunction()};

var header = document.getElementById("header");
var sticky = header.offsetTop;

function myFunction() {
  if (window.pageYOffset > sticky) {
    header.classList.add("sticky");
  } else {
    header.classList.remove("sticky");
  }
}

document.getElementById("zoomIn").addEventListener('click', function(e){
    Array.from(info).forEach( function( elementInfo ){
        const viewport = cornerstone.getViewport( elementInfo[0] );
        viewport.scale+=0.25;
        cornerstone.setViewport( elementInfo[0], viewport);
    });
});   
document.getElementById("reviewFiles").addEventListener('click', function(e){
    folderPath = getParentDirectory();
    $('input[name="1-219.dcm"]:checked').val();
    reviewInfo=[];
    for( i = 0 ; i < reviewIds.length; i++ )
    {   
        info = []
        info.push( folderPath );
        info.push( reviewIds[i] + ".dcm" );
        info.push( $("input[name='" + reviewIds[i]+ ".dcm' ]:checked").val() );
        reviewInfo.push( info )
    }
    csvContent = ""
    reviewInfo.forEach(function(rowArray) {
    let row = rowArray.join(",");
    csvContent += row + "\r\n";
    });
    const el = document.createElement('textarea');
          el.value = csvContent;
          document.body.appendChild(el);
          el.select();
          document.execCommand('copy');
          document.body.removeChild(el);
}); 


document.getElementById("zoomOut").addEventListener('click', function(e){
    Array.from(info).forEach( function( elementInfo ){
        const viewport = cornerstone.getViewport( elementInfo[0] );
        viewport.scale-=0.25;
        cornerstone.setViewport( elementInfo[0], viewport);
    });
});

document.getElementById("resetZoom").addEventListener('click', function(e){
    Array.from(info).forEach( function( elementInfo ){
        cornerstone.reset(elementInfo[0]);
    });
});  

function checkBoxExcludeClick( e )
{
    var id = e.id.substr( 0, e.id.lastIndexOf("." ) );
    if( e.checked )
        checkInIds.push( id );
    else
        checkInIds = checkInIds.filter(checkBoxId => checkBoxId !== id);
var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
checkInIds.sort(collator.compare);
deactivateImages();
}
function checkBoxReviewClick( e )
{
    var parentElement = e.parentElement.parentElement.parentElement;
    var parentBorderColor = parentElement.style.borderColor;
    var id = e.id.substr( 0, e.id.lastIndexOf("." ) );
    if( e.checked )
    {      reviewIds.push( id );
          parentElement.style.border="dotted";
          parentElement.style.borderColor=parentBorderColor
    }
    else
    {
        reviewIds = reviewIds.filter(reviewId => reviewId !== id);
        parentElement.style.border="ridge";
    } 
    parentElement.style.borderColor=parentBorderColor;
    
}
function deactivateImages()
{
    Array.from(document.getElementsByClassName('inactive')).forEach(function(el) { 
        el.classList.remove('inactive');
    });

    if( checkInIds.length >= 2 )
        {
            start = false
            for( i = 0 ; i < info.length; i++ )
            {
                id =  info[i][0].id;
                divId = id.substr( 0, id.lastIndexOf("." ) );
                if( divId == checkInIds[0] )
                        start = true;
                if( start )
                    info[i][0].classList.add("inactive");
                if( divId == checkInIds[checkInIds.length-1] )
                    break;
            }
        }
}
