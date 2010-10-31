function init_history()
{
  
  _in = document.getElementById("input-field");
  _out = document.getElementById("output-area");
  //refocus();
}

function refocus(ln)
{
  if (!ln)
  {
      anchor = 'focuspoint';
  }
  else
  {
  	if (ln < 8) {
  	    anchor = '1'
  	}
  	else {
  	    anchor = ln - 3;
  	}
  }
  try {
      location.hash = anchor;
      //location.hash = "footer-focus";
      setTimeout("_in.focus();",0);
  } catch(e) {
      //pass
  }
}

function hist(up)
{
  // histList[0] = first command entered, [1] = second, etc.
  // type something, press up --> thing typed is now in "limbo"
  // (last item in histList) and should be reachable by pressing 
  // down again.

  var L = histList.length;

  if (L == 1)
    return;

  if (up)
  {
    if (histPos == L-1)
    {
      // Save this entry in case the user hits the down key.
      histList[histPos] = _in.value;
    }

    if (histPos > 0)
    {
      histPos--;
      // Use a timeout to prevent up from moving cursor within new text
      // Set to nothing first for the same reason
      setTimeout(
        function() {
          _in.value = ''; 
          _in.value = histList[histPos];
          var caretPos = _in.value.length;
          if (_in.setSelectionRange) 
            _in.setSelectionRange(caretPos, caretPos);
        },
        0
      );
    }
  } 
  else // down
  {
    if (histPos < L-1)
    {
      histPos++;
      _in.value = histList[histPos];
    }
    else if (histPos == L-1)
    {
      // Already on the current entry: clear but save
      if (_in.value)
      {
        histList[histPos] = _in.value;
        ++histPos;
        _in.value = "";
      }
    }
  }
}

function caretInFirstLine(textbox)
{
  // IE doesn't support selectionStart/selectionEnd
  if (textbox.selectionStart == undefined)
    return true;

  var firstLineBreak = textbox.value.indexOf("\n");
  
  return ((firstLineBreak == -1) || (textbox.selectionStart <= firstLineBreak));
}

function caretInLastLine(textbox)
{
  // IE doesn't support selectionStart/selectionEnd
  if (textbox.selectionEnd == undefined)
    return true;

  var lastLineBreak = textbox.value.lastIndexOf("\n");
  
  return (textbox.selectionEnd > lastLineBreak);
}

registerPloneFunction(init_history);
