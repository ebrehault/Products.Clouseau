/* 
 * Clouseau Client Processor
 *
 * Written mostly by Andy McKay with original assistance from
 * Richard Amerman.
 *
 * Query String parser by Peter A. Bromberg, Ph.D.
 *    Taken from: http://www.eggheadcafe.com/articles/20020107.asp
 *
 */


function getInput() {
    return document.getElementById("input-field");
}

function getOutput() {
    return document.getElementById("output-table");
}

function getInputRow() {
    return document.getElementById("input-row");
}

function getTipOutput() {
    return document.getElementById("tip-output");
}

function getTipDocumentationOutput() {
    return document.getElementById("tip-output");
}

function LZ(x) {
    return (x >= 10 || x < 0 ? "" : "0") + x;
}

function LZZ(x) {
    return x < 0 || x >= 100 ? "" + x : "0" + LZ(x);
}

var _session_id = null;
var _ln = 0; // local client line count
var _sln = 0; // remote server line count
var _first_prompt = ">>> ";
var _second_prompt = "... ";
var _prompt_hold = false;
var _prompt = _first_prompt;
var _indent = 0; // the indent
// histlist, not sure what these do
var histList = [""]; 
var histPos = 0; 
var _in = null;
var _out = null;
var _fp = null;
// cache for Tips
var _tip_cache = Array();
var _tip_current = "";
var _tip_cause = false;
var _tip_autocomplete = Array();
var _context = "";
var _valid_session = true;

function endswith(str, chr) {
    if (str.charAt(str.length-1) == chr) {
        return true;
    }
    return false;
}

function gotSession() {
    //TODO Add support for i18n on this string
    setMessage("Got a session, id:" + _session_id);
    var input = getInput();
    input.style.display = "inline";
    checkStatus();
    // this is where it polls contintually for status
    // if the status fails we should stop the polling.
    setInterval(checkStatus, 1000);
    
    var msg_id = document.getElementById("session-id");
    var msg_link = document.getElementById("session-link");
    var msg_xml_link = document.getElementById("session-xml-link");
    var msg_text_link = document.getElementById("session-text-link");
    var delete_link = document.getElementById("session-delete")
    var save_link = document.getElementById("session-save");
    
    if (msg_id) {
        msg_id.innerHTML = _session_id;
        if (msg_link) {
            msg_link.href = "clouseau_view?session_id=" + _session_id;
        }
        if (msg_xml_link) {
            msg_xml_link.href = "clouseau_tool/get_all_lines_xml?session_id=" + _session_id;
        }
        if (msg_text_link) {
            msg_text_link.href = "clouseau_tool/get_all_lines_text?session_id=" + _session_id;
        }
        if (delete_link) {
            delete_link.href = "clouseau_tool/stop_session?session_id=" + _session_id;
        } 
        if (save_link) {
            save_link.href = "clouseau_tool/save_session?session_id=" + _session_id;
        }
    }
    
    tipProcess("dir()", "", false);
}

function clouseauChange(display) {
    elements = cssQuery(".output-row");
    for (var k = 0; k < elements.length; k++) {
        elements[k].style.display = display;
    }
    return false;
}

function loadFilename() {    
    var filename = getString("filename");
    if (filename != "null") {    
        var req = new XMLHttpRequest()
        req.onreadystatechange = function() {
            if(req.readyState == 4) {
                if (req.status != 200) {
                    //TODO Add support for i18n on this string
             //       setMessage("Error occurred trying to load a saved session" , "error");
                };
            };
        };
    
        req.open("POST", "clouseau_tool/load_session", true);
        if (_context == null) {
            req.send("");
        } else {
            req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            req.send("session_id=" + _session_id + "&filename=" + filename);
        }
        //TODO Add support for i18n on this string
        setMessage("Loading from saved session please wait...");
    };
}

function getSession() {
    // hide the javascript warning
    var warning = document.getElementById("clouseau-warning");
    warning.style.display = "none";
    
    // would be helpful if we could hide this in the pt, oh well.
    var left = document.getElementById("portal-column-one")
    if (left) {
        left.style.display = "none";
    }
    
    
    _session_id = getString("session_id");
    _context = getString("context");
    if (_session_id != "null") {
        // yay start the check status loop
        gotSession();
        return;
    }
    
    var req = new XMLHttpRequest()
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            if (req.status != 200) {
                //TODO Add support for i18n on this string
                setMessage("Error occured trying to create new session: " + req.statusText + " (" + req.status + ")." , "error");
            } else {
                var xml = req.responseXML.documentElement;
                var session = xml.getElementsByTagName("session")[0];
                _session_id = session.getAttribute("id");
                gotSession();
                loadFilename();
            };
        };
    };
    req.open("POST", "clouseau_tool/new_session_xml", true);
    if (_context == null) {
        req.send("");
    } else {
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        req.send("context=" + _context);
    }
    //TODO Add support for i18n on this string
    setMessage("Getting a session with context of " + _context + " please wait...");
    setTimeout(reFocus, 0);
}

function checkStatus() {
    if (!_valid_session) {
       // the use of clearInterval should but 
       // in Safari didn't seem to
       clearInterval(checkStatus);
       return false;
    }
    var req = new XMLHttpRequest();
    //debugging mode
    
    req.onreadystatechange = function() {
        //alert(req.readyState);
        if(req.readyState == 4) {
            if (req.status != 200) {
                // error!
                _valid_session = false;
                //TODO Add support for i18n on this string
                setMessage("Error occured trying to get status: " + req.statusText + " (" + req.status + "). Stopped checking status." , "error");
            } else {
                var xml = req.responseXML.documentElement;
                var session= xml.getElementsByTagName("session")[0];
                _sln = session.getAttribute("lines");
                //debugging mode
                //TODO Add support for i18n on this string
                //setMessage("Server has " + _sln + " lines and the client has " + _ln + " lines.", "debug")
                if (_sln > _ln) {
                    getLines();
                }
            };
        };
    };
    req.open("POST", "clouseau_tool/get_session_xml", true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send("session_id=" + _session_id);
}

function sendText(text) {
    // if we have no session id, then we exit
    if (!_session_id) {
        return false;
    }
    text = encodeURIComponent(text);
    var req = new XMLHttpRequest()
    
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            if (req.status != 200) {
                //TODO Add support for i18n on this string
                setMessage("Error occured trying send text to the server: " + req.statusText + " (" + req.status + ")." , "error");
            }
        };
    };
    req.open("POST", "clouseau_tool/process_text_xml", true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send("session_id=" + _session_id + "&text=" + text);
}

function maybeProcessAutoComplete(show, complete) {
    // if we have no session id, then we exit
    if (!_session_id) {
        return false;
    }
    var text = getInput();
    text = text.value;
    if (text.length < 1) {
        return
    }
    // find the .
    var lastDot = text.lastIndexOf(".");
    var lastLine = text.lastIndexOf("\n");
    if (lastLine > 0) {
        text = text.slice(lastLine + 1, text.length);
    }
    if (lastDot < 0) {
        findAutoComplete(text, show, complete);
    } else {
        text = text.slice(lastDot + 1);
        if (text.length > 0) {
            findAutoComplete(text, show, complete);
        }
    }
}

function maybeProcessTip() {
    // if we have no session id, then we exit
    if (!_session_id) {
        return false;
    }
    var text = getInput();
    text = text.value;
    var lastChar = text.charAt(text.length - 1);
    var lastLine = text.lastIndexOf("\n");
    if (lastLine > 0) {
        text = text.slice(lastLine + 1, text.length);
    }
    
    if (lastChar == "(") {
        // if we get an opening bracket, try and trigger a check
        tipProcess(text.slice(0, -1), "(", true);
        return;
    } else if (lastChar == ")") {
        // if we closed the ) then we want to close tip
        disableTip();
        return;
    } else if (lastChar == ".") {
        // if we aren't in (, try and trigger a 
        // object tooltip 
        disableTip();
        if (_tip_cause != "(") {
            tipProcess(text.slice(0, -1), ".", true);
            return;
        }
    } else {
        var re = new RegExp("^\\w+$");
        // better way to test this?
        if (re.test(lastChar)) {
            // pass no sure if we want to do anything here
        } else {
            // if we have something thats not
            // a valid variable name and we are in
            // a variable tooltip, then close tooltip
            if (_tip_cause == ".") {
                disableTip();
                return;                
            }
        }
    }
}

function tipProcess(text, cause, check) {
    disableTip();
    _tip_cause = cause;
    if (check) {
        if (text == _tip_current) {
            // no need to update anything
            return;
        }
        
        /* trim it, then apply a cache */
        text = encodeURIComponent(text);
        
        if (_tip_cache[text]) {
            enableTip(text);
            return;
        }
    }
    var req = new XMLHttpRequest()
    
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            if (req.status != 200) {
                //TODO Add support for i18n on this string
                setMessage("Warning possible syntax error. Error occured trying to get a tool tip from the server.");
            } else {
                // get the data from the XML
                var xml = req.responseXML.documentElement;
                xml.normalize();
                var docs_data = new Array;
                var docs = xml.getElementsByTagName("tip");
                
                for (var k = 0; k < docs.length; k++) {
                    var elem = docs[k];
                    var data = "";
                    try { data = elem.firstChild.data } catch (e) {};
                    docs_data.push(Array(elem.getAttribute("id"), data));
                }
                
                // set the current and the cache
                _tip_cache[text] = docs_data;
                enableTip(text);
            }
        };
    };
    req.open("POST", "clouseau_tool/get_tip_xml", true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send("session_id=" + _session_id + "&text=" + text);        
}

function disableTip() {
    var out = getTipDocumentationOutput();
    out.style.display = ""; 
    out.innerHTML = "";
    // clear cache
    _tip_current = ""; 
    _tip_cause = false;
}

function findAutoComplete(text, show, complete) {
    closest = "";
    var text_length = text.length;
    if (text_length < 1) {
        return;
    }
    var lastLine = text.lastIndexOf("\n");
    if (lastLine > 0) {
        text = text.slice(lastLine + 1, text.length);
    }
    
    for (var k = 0; k < _tip_autocomplete.length; k++) {
            var tip = _tip_autocomplete[k];
            var tip_slice = tip.slice(0, text_length);
            //alert(tip + ":" + text_length + ":" + tip_slice + ":" + text);
            if (tip_slice == text) {
                closest = tip;
                break;
            }

    }
    
    var rest = closest.slice(text_length);
    var inp = getInput();
    var value = inp.value;


    if (show) {
        //TODO Add support for i18n on this string
        setMessage(value, "autocomplete", "autocomplete-start");
        //TODO Add support for i18n on this string
        setMessage(rest, "autocomplete", "autocomplete-rest");
    }
    if (complete) {        
        inp.value = value + rest;
        caretPos = inp.value.length;
        inp.setSelectionRange(caretPos, caretPos);
    }
}

function enableTip(text) {
    // set caches
    _tip_current = text;
    // reset autocomplete
    _tip_autocomplete = Array()
    
    // flip
    var tip = _tip_cache[text];
    var out = getTipOutput();
    out.style.display = "block";
    var doc_out = getTipDocumentationOutput();
    for (var k = 0; k < tip.length; k++) {
        var term = document.createElement("dt");
        var defn = document.createElement("dd");
        term.innerHTML = tip[k][0];
        defn.innerHTML = tip[k][1].replace(/\n/g, "<br />");
        var tips = tip[k][1].split(',');
        for (var i = 0; i < tips.length; i++) {
            _tip_autocomplete.push(tips[i].replace(/ /g, ""));
        }
        doc_out.appendChild(term);
        doc_out.appendChild(defn);        
    }
    _tip_autocomplete.sort();
}

function getLines() {
    // if we have no session id, then we exit
    if (!_session_id) {
        return false;
    }

    var req = new XMLHttpRequest()
    
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            // alert(req.responseText);
            
            if (req.status != 200) {
                // error!
                //TODO Add support for i18n on this string
                setMessage("Error occured trying to get lines: " + req.statusText + " (" + req.status + ")." , "error");
            } else {
                var xml = req.responseXML.documentElement;
                xml.normalize();
                var lines = xml.getElementsByTagName("line");
                for (var x = 0; x < lines.length; x++) {
                    var command = lines[x].getElementsByTagName("command");
                    var response = lines[x].getElementsByTagName("response");                    
                    var status = lines[x].getAttribute("status");
                    if (status == "input-not-complete") {
                        setPrompt("second");
                    } else {
                        setPrompt("first");
                    }
                    /* if there is a command, or a command and no reponse... */
                    if (command.length > 0) { 
                        var cmd = null;
                        try {
                            cmd = command[0].firstChild.data;
                        }
                        catch (e) {
                            cmd = '';
                        }
                        processOutputLine(cmd, true);
                    }
                    /* if there is no command and response, we've got a blank line */
                    if ((command.length == 0) && (response.length == 0)) {
                        processOutputLine('', true);
                    }
                    if (response.length > 0) {
                        var res = null;
                        try {
                            res = response[0].firstChild.data;
                        }
                        catch (e) {
                            res = '';
                        }
                        processOutputLine(res, false);
                    }
                    // for each line we have increment server count
                    _ln += 1
                };
                //TODO Add support for i18n on this string
                setMessage("Done, waiting for input");
            };
            var input = getInput();
            input.style.display = "inline";   
            refocus(_ln);
        };
    };

    req.open("POST", "clouseau_tool/get_lines_xml", true);

    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var lines_query = "";
    for (var k = _ln; k < _sln; k++) {
        lines_query += "&line_numbers:list=" + k;
    }
    //TODO Add support for i18n on this string
    setMessage("Getting lines, server is at " + _sln + " client is at " + _ln);
    req.send("session_id=" + _session_id + lines_query);
}

function setPrompt(type) {
    var prompt = document.getElementById("input-prompt");
    if (type == "first") {
        _prompt_hold = false;
        _prompt = _first_prompt;
        prompt.innerHTML = _first_prompt;
    } else {
        if (_prompt_hold == false) {
            _prompt_hold = true;
        } else {
            _prompt_hold = false;
            _prompt = _second_prompt;
            prompt.innerHTML = _second_prompt;
        }
    }
}

function processOutputLine(text, add_prompt) {
    var output = getOutput();
    var input_row = getInputRow();
    
    var code = document.createElement("code");    
    var prompt_code = document.createElement("code");
    
    var output_row = document.createElement("tr");
    var ln_td = document.createElement("td");
    var line_number = document.createElement("a");
    var prompt_td = document.createElement("td");
    var output_td = document.createElement("td");
    
    line_number.name = _ln;
    var new_ln = _ln;
    line_number.innerHTML = LZZ(new_ln + 1);
    line_number.className = "clouseau-line-number";
    
    prompt_code.innerHTML = _prompt;
    prompt_td.appendChild(prompt_code);
    
    ln_td.className = "output-cell";
    ln_td.appendChild(line_number);
    output_row.className = "output-row";
    output_td.className = "output-cell";
    output_row.appendChild(ln_td);
    
    if (add_prompt == true) {
        prompt_td.className = "output-cell";
        output_row.appendChild(prompt_td);
    } else {
        output_td.colSpan = 2;
    }
    prompt_code.className = "clouseau-prompt";
    code.id = "hidden-code-line-" + new_ln;
    code.innerHTML = text;
    output_td.appendChild(code);
    output_row.appendChild(output_td);
    input_row.parentNode.insertBefore(output_row,input_row);

    if (text.length < 2000) {
        dp.SyntaxHighlighter.HighlightClouseau(code, text);
    } else {
        var large_result = document.createElement("a");
        //TODO Add support for i18n on this string
        large_result.innerHTML = text.substring(0, 200) + " ...large result truncated, click to expand";
        large_result.id = "truncated-code-line-" + new_ln;
        large_result.setAttribute("class", "truncated-none");
        large_result.onclick = toggleHiddenCode;
        /* dp syntax highlighter does this for us,
        but we need to manually do it,
        this is a bit ugly roger
        */
        code.innerHTML = code.innerHTML.replace(/&/g,'&amp;').replace(/>/g,'&gt;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
        code.style.display = 'none';
        code.parentNode.insertBefore(large_result, code);
    }
    
}

function toggleHiddenCode() {
    var id = this.id;
    var trans = "hidden-code-line-" + id.substring("truncated-code-line-".length);
    var element = document.getElementById(trans);
    
    var cur_style = element.style.display;
    var new_style = null;
    if (cur_style == "block") {
        new_style = "none";
    } else {
        new_style = "block";
    }
    this.setAttribute("class", "truncated-" + new_style);
    element.style.display = new_style
}

function showHiddenCode() {
    toggleHiddenCode("block");
}

function hideHiddenCode() {
    toggleHiddenCode("none");
}


function setMessage(text, type, id) {
    if (!type) {
        type = "info";
    }
    if (!id) {
        id = "message";
    }
    var msg = document.getElementById(id);
 
    msg.innerHTML = text;
    msg.className = "clouseau-" + type;   
}

function process() {
    var input = getInput();
    var text = input.value;
    
    histList[histList.length-1] = text;
    histList[histList.length] = "";
    histPos = histList.length - 1;
        
    //TODO Add support for i18n on this string
    setMessage("Processing...");
    sendText(text);
    input.value = '';
    tipProcess("dir()", "", false);
    return false;
}

function PageQueryObject(q) {
    if(q.length > 1) {
        this.q = q.substring(1, q.length);
    } else {
        this.q = null;
    }
    this.keyValuePairs = new Array();
    if(q) {
        for(var i=0; i < this.q.split("&").length; i++) {
            this.keyValuePairs[i] = this.q.split("&")[i];
        }
    }
    this.getKeyValuePairs = function() { return this.keyValuePairs; }
    this.getValue = function(s) {
        for(var j=0; j < this.keyValuePairs.length; j++) 
        {
            if(this.keyValuePairs[j].split("=")[0] == s)
            return this.keyValuePairs[j].split("=")[1];
        }
        return null;
    }

    this.getParameters = function() {
        var a = new Array(this.getLength());
        for(var j=0; j < this.keyValuePairs.length; j++)
        {
            a[j] = this.keyValuePairs[j].split("=")[0];
        }
        return a;
    }
    this.getLength = function() { return this.keyValuePairs.length; }
}

function getString(key) {
    var page_object = new PageQueryObject(window.location.search);
    return unescape(page_object.getValue(key));
}

function reFocus() {
    // a desperate attempt to get this to work on
    // Safari
    var inp = getInput();
    inp.blur();   
    inp.focus();
};

function inputKeydown(e) {
    // this is a tab
    if (e.keyCode == 9) {
        maybeProcessAutoComplete(false, true);
        setTimeout(reFocus, 0);
        return false;
    }
}

function inputKeyup(e) {     
    maybeProcessTip();
    if (_tip_autocomplete.length >= 1) {
        maybeProcessAutoComplete(true, false);
    }
    

    // this is an enter
    if (e.keyCode == 13) {
       process();
       // hid the tool tip
       disableTip();
       setTimeout(reFocus, 0);
       return false;
    } 

    if (e.keyCode == 38) { // up
      // go up in history if at top or ctrl-up 
      if (e.ctrlKey || caretInFirstLine(_in))

        hist(true);
    } else if (e.keyCode == 40) { // down
      // go down in history if at end or ctrl-down
      if (e.ctrlKey || caretInLastLine(_in))
        hist(false);
    }
    return false;
};



registerPloneFunction(getSession);
