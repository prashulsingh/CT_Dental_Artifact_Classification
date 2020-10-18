
$(document).ready(function() {

    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

});
var i =0;
var info=[];
var csvFilesFound = [];
function showDicomFiles(context)
{
    var filesList = document.getElementById( 'client-files' ).files;
    if( Array.from(filesList).length == 0 )
        return;
    csvFilesFound = [];
    checkInIds=[]
    
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
            csvFilesFound.push( fileName );
        }

    });

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
    annotationFiles.innerHTML = csvFilesFound.toString();
    
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
          $(this).parent().parent()[0].style.borderColor="yellow";
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
    '<div id=\"' + fileName + "_img_holder" + '\" style="width:99%;height:94%;top:0px;left:0px; position:absolute">',
    '</div>',
    '<div id=\"' + fileName + "_img_name" + '\" style="position:absolute;top:0px;left:0px;color:white">',
    '</div>',
    '<div style="top:330px;width:100%; position:absolute; display:inline;color:black;margin:0px;">',
    '<input  checked type="radio"  name=\"' + fileName + '\" value="low" />',
        '<label for="one">Low</label>',
        '<input  type="radio" style="margin-left:25%" name=\"' + fileName + '\" value="medium" />',
        '<label for="two">Medium</label>',
        '<input onchange="myFunction()" type="radio"  style=\"margin-left:17%\"name=\"' + fileName + '\" value="high" />',
        '<label for="two">High</label>',
        '<input type=\"checkbox\" id=\"' + fileName + "_checkbox" + '\"  onclick=\"checkBoxClick(this)\" style=\"margin-left: 2%\">',    
    '</div>',
'</div >' 
].join("\n");

   // console.log( htmlString );
    return htmlString;

}

function validFile( fileInfo  )
{
    return fileInfo.name.endsWith( ".dcm" );
}

function getParentDirectory(){
    var folderPath = document.getElementById( 'folder-url' ).value;

    if( typeof(folderPath) == 'undefined' || folderPath === null || folderPath == ""   )
        alert( 'Please provide valid folder folder path containig DICOM Images ');
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
    console.log( content );
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
checkInIds=[];
function checkBoxClick( e )
{
    var id = e.id.substr( 0, e.id.lastIndexOf("." ) );
    if( e.checked )
        checkInIds.push( id );
    else
        checkInIds = checkInIds.filter(checkBoxId => checkBoxId !== id);
var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
checkInIds.sort(collator.compare);
deactivateImages();
console.log( checkInIds );
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
