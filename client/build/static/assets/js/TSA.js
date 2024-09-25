"use strict";
// import { API_URL } from './demo';
const rpa_url = ''

// Setting Color

$(window).resize(function() {
	$(window).width(); 
});

$('.changeBodyBackgroundFullColor').on('click', function(){
	if($(this).attr('data-color') == 'default'){
		$('body').removeAttr('data-background-full');
	} else {
		$('body').attr('data-background-full', $(this).attr('data-color'));
	}

	$(this).parent().find('.changeBodyBackgroundFullColor').removeClass("selected");
	$(this).addClass("selected");
	layoutsColors();
});

$('.changeLogoHeaderColor').on('click', function(){
	if($(this).attr('data-color') == 'default'){
		$('.logo-header').removeAttr('data-background-color');
	} else {
		$('.logo-header').attr('data-background-color', $(this).attr('data-color'));
	}

	$(this).parent().find('.changeLogoHeaderColor').removeClass("selected");
	$(this).addClass("selected");
	customCheckColor();
	layoutsColors();
});

$('.changeTopBarColor').on('click', function(){
	if($(this).attr('data-color') == 'default'){
		$('.main-header .navbar-header').removeAttr('data-background-color');
	} else {
		$('.main-header .navbar-header').attr('data-background-color', $(this).attr('data-color'));
	}

	$(this).parent().find('.changeTopBarColor').removeClass("selected");
	$(this).addClass("selected");
	layoutsColors();
});

$('.changeSideBarColor').on('click', function(){
	if($(this).attr('data-color') == 'default'){
		$('.sidebar').removeAttr('data-background-color');
	} else {
		$('.sidebar').attr('data-background-color', $(this).attr('data-color'));
	}

	$(this).parent().find('.changeSideBarColor').removeClass("selected");
	$(this).addClass("selected");
	layoutsColors();
});

$('.changeBackgroundColor').on('click', function(){
	$('body').removeAttr('data-background-color');
	$('body').attr('data-background-color', $(this).attr('data-color'));
	$(this).parent().find('.changeBackgroundColor').removeClass("selected");
	$(this).addClass("selected");
});

function customCheckColor(){
	var logoHeader = $('.logo-header').attr('data-background-color');
	if (logoHeader !== "white") {
		$('.logo-header .navbar-brand').attr('src', '/static/assets/img/logo.svg');
	} else {
		$('.logo-header .navbar-brand').attr('src', '/static/assets/img/logo2.svg');
	}
}


var toggle_customSidebar = false,
custom_open = 0;

if(!toggle_customSidebar) {
	var toggle = $('.custom-template .custom-toggle');

	toggle.on('click', (function(){
		if (custom_open == 1){
			$('.custom-template').removeClass('open');
			toggle.removeClass('toggled');
			custom_open = 0;
		}  else {
			$('.custom-template').addClass('open');
			toggle.addClass('toggled');
			custom_open = 1;
		}
	})
	);
	toggle_customSidebar = true;
}

function set_table() {
	$('#TSA-Table').DataTable({
		"pageLength": 5,
		initComplete: function () {
			this.api().columns().every(function () {
				var column = this;
				console.log(column)
				var select = $('<select class="form-control"><option value=""></option></select>')
					.appendTo($(column.footer()).empty())
					.on('change', function () {
						var val = $.fn.dataTable.util.escapeRegex(
							$(this).val()
						);

						column
							.search(val ? '^' + val + '$' : '', true, false)
							.draw();
					});

				column.data().unique().sort().each(function (d, j) {
					select.append('<option value="' + d + '">' + d + '</option>')
				});
			});
		}
	});
}
// $(document).ready(function () {
	
// 	});

// 	// Add Row
// 	$('#add-row').DataTable({
// 		"pageLength": 5,
// 	});

// 	var action = '<td> <div class="form-button-action"> <button type="button" data-toggle="tooltip" title="" class="btn btn-link btn-primary btn-lg" data-original-title="Edit Task"> <i class="fa fa-edit"></i> </button> <button type="button" data-toggle="tooltip" title="" class="btn btn-link btn-danger" data-original-title="Remove"> <i class="fa fa-times"></i> </button> </div> </td>';

// 	$('#addRowButton').click(function () {
// 		$('#add-row').dataTable().fnAddData([
// 			$("#addName").val(),
// 			$("#addPosition").val(),
// 			$("#addOffice").val(),
// 			action
// 		]);
// 		$('#addRowModal').modal('hide');

// 	});
// });
$(document).ready(function () {
	$.get('/tsaDash', function (data) {
		print_data(data);
		set_table();
		// $('#TSA-Table').DataTable({
		// 	"pageLength": 5,
		// 	initComplete: function () {
		// 		this.api().columns().every(function () {
		// 			var column = this;
		// 			console.log(column)
		// 			var select = $('<select class="form-control"><option value=""></option></select>')
		// 				.appendTo($(column.footer()).empty())
		// 				.on('change', function () {
		// 					var val = $.fn.dataTable.util.escapeRegex(
		// 						$(this).val()
		// 					);
	
		// 					column
		// 						.search(val ? '^' + val + '$' : '', true, false)
		// 						.draw();
		// 				});
	
		// 			column.data().unique().sort().each(function (d, j) {
		// 				select.append('<option value="' + d + '">' + d + '</option>')
		// 			});
		// 		});
		// 	}
		// });
	});
	$("#loaderDiv").hide();

	$('#dateRangeForm').submit(function (event) {
		event.preventDefault();
		var formData = $(this).serialize();
		
		$.ajax({
			url: '/tsaDash',
			type: 'POST',
			data: formData,
			beforeSend: function () {
				$('#TSA-Table tbody').empty();
				// Generating();
				$("#loaderDiv").show();
			},
			success: function (data) {
				$('#TSA-Table tbody').empty();
				$("#loaderDiv").hide();
				print_data(data)  
				//set_table()                      
				console.log(data);
			},
			error: function (xhr, status, error) {
				console.log(error);
			}
		});
	});
});

function print_data(data) {
	$.each(data, function (index, process) {
		var row = $('<tr>');
		row.append($('<td>').text(process.Event_Date));
		//alterfunction, altertrigger, 
		var Event = $('<td>');
		try {
			if (process.Event_Type.includes('alter_function')) {
				Event.text(process.Event_Type).addClass('linen');
			} else if (process.Event_Type.includes('alter_index')) {
				Event.text(process.Event_Type).addClass('salmon');
			} else if (process.Event_Type.includes('alter_procedure')) {
				Event.text(process.Event_Type).addClass('palegoldenrod');
			} else if (process.Event_Type.includes('alter_table')) {
				Event.text(process.Event_Type).addClass('peachpuff');
			} else if (process.Event_Type.includes('alter_trigger')) {
				Event.text(process.Event_Type).addClass('mistyrose');
			} else if (process.Event_Type.includes('alter_view')) {
				Event.text(process.Event_Type).addClass('pink');
			} else if (process.Event_Type.includes('create_function')) {
				Event.text(process.Event_Type).addClass('lavender');
			} else if (process.Event_Type.includes('create_index')) {
				Event.text(process.Event_Type).addClass('honeydew');
			} else if (process.Event_Type.includes('create_procedure')) {
				Event.text(process.Event_Type).addClass('cornsilk');
			} else if (process.Event_Type.includes('create_schema')) {
				Event.text(process.Event_Type).addClass('lightyellow');
			} else if (process.Event_Type.includes('create_table')) {
				Event.text(process.Event_Type).addClass('beige');
			} else if (process.Event_Type.includes('create_user')) {
				Event.text(process.Event_Type).addClass('thistle');
			} else if (process.Event_Type.includes('drop_index')) {
				Event.text(process.Event_Type).addClass('lightgray');
			} else if (process.Event_Type.includes('drop_procedure')) {
				Event.text(process.Event_Type).addClass('mintcream');
			} else if (process.Event_Type.includes('drop_table')) {
				Event.text(process.Event_Type).addClass('lavenderblush');
			} else if (process.Event_Type.includes('drop_user')) {
				Event.text(process.Event_Type).addClass('peru');
			} else if (process.Event_Type.includes('grant_database')) {
				Event.text(process.Event_Type).addClass('cornsilk');
			} else if (process.Event_Type.includes('rename')) {
				Event.text(process.Event_Type).addClass('mediumturquoise');
			} else if (process.Event_Type.includes('update_statistics')) {
				Event.text(process.Event_Type).addClass('aquamarine');
			} else {
				Event.text(process.Event_Type);
			}
		} catch (error) {
			Event.text('Null');
		}
		row.append(Event);
		
		var Schema = $('<td>');
		try {
			if (process.Schema_Name.includes('fdy')) {
				Schema.text(process.Schema_Name).addClass('cornsilk');
			} else if (process.Schema_Name.includes('book')) {
				Schema.text(process.Schema_Name).addClass('salmon');
			} else if (process.Schema_Name.includes('rpa')) {
				Schema.text(process.Schema_Name).addClass('lavenderblush');
			} else if (process.Schema_Name.includes('roof')) {
				Schema.text(process.Schema_Name).addClass('peachpuff');
			} else if (process.Schema_Name.includes('stg')) {
				Schema.text(process.Schema_Name).addClass('mintcream');
			} else if (process.Schema_Name.includes('tbd')) {
				Schema.text(process.Schema_Name).addClass('lightgray');
			} else if (process.Schema_Name.includes('predict')) {
				Schema.text(process.Schema_Name).addClass('mistyrose');
			} else if (process.Schema_Name.includes('Null')) {
				Schema.text(process.Schema_Name).addClass('gray');
			} else if (process.Schema_Name.includes('tsa')) {
				Schema.text(process.Schema_Name).addClass('plum');
			} else if (process.Schema_Name.includes('uam')) {
				Schema.text(process.Schema_Name).addClass('lightyellow');
			} else if (process.Schema_Name.includes('windmar')) {
				Schema.text(process.Schema_Name).addClass('lavender');
			} else if (process.Schema_Name.includes('com')) {
				Schema.text(process.Schema_Name).addClass('thistle');
			} else if (process.Schema_Name.includes('dbo')) {
				Schema.text(process.Schema_Name).addClass('beige');
			} else if (process.Schema_Name.includes('wolf')) {
				Schema.text(process.Schema_Name).addClass('honeydew');
			} else {
				Schema.text(process.Schema_Name);
			}
		} catch (error) {
			Schema.text('Null').addClass('peru')
		}

		row.append(Schema);

		row.append($('<td>').text(process.Object_Name));
		row.append($('<td>').text(process.Host_Name));
		row.append($('<td>').text(process.IPAddress));
		row.append($('<td>').text(process.Program_Name));
		row.append($('<td>').text(process.Login_Name));

		var collapsibleRow = $('<tr class="collapsible collapsed">');
		var collapsibleCell = $('<td colspan="8">');
		collapsibleCell.html('Event DDL: ' + process.Event_XML.replace(/\n/g, '<br>'));
		collapsibleRow.append(collapsibleCell);
		row.click(function () {
			collapsibleRow.toggle();
			collapsibleRow.insertAfter(row);
		});
		$('#TSA-Table tbody').append(row);
		$('#TSA-Table tbody').append(collapsibleRow);
		//$('#TSA-Table tbody').append(row);
	});
}
// $(document).ready(function () {
// 	console.log("yes")
	// $.get(rpa_url, function (data) {
	// 	// bot_data = data; //assign global bot data to data function
	// 	bot_data = data;
	// 	// console.log(bot_data);
	// 	process_table(bot_data);
	// 	$.each(bot_data, function (index, process) {
	// 		if (process.Running.includes("Yes")) {
	// 			total_running += 1;
	// 		} else if (process.Running.includes("Not Running")) {
	// 			total_not_running += 1;
	// 		} else if (process.Running.includes("Not Updating")) {
	// 			total_not_updating += 1
	// 		} else {
	// 			//pass
	// 		}
	// 	});
