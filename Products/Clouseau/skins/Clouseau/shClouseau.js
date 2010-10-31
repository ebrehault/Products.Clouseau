/*

Addition to highlight just a specific element with specific code with Python

*/

dp.sh.HighlightClouseau = function(element, code) {
    var highlighter = null;
	var registered = new Object();
	var propertyName = 'value';
	
    for(var brush in dp.sh.Brushes)
	{
		var aliases = dp.sh.Brushes[brush].Aliases;
		
		if(aliases == null)
			continue;
		
		for(var i = 0; i < aliases.length; i++)
			registered[aliases[i]] = brush;
	};
	
    highlighter = new dp.sh.Brushes[registered["python"]]();
    element.style.display = 'none';

	highlighter.addGutter = false;
	highlighter.addControls = false;
	highlighter.collapse = false;
	highlighter.Highlight(code);

	// place the result table inside a div
	var div = document.createElement('DIV');
	
	div.className = 'dp-highlighter';
	div.appendChild(highlighter.table);

	element.parentNode.insertBefore(div, element);
}