$.fn.isOnScreen = function(){
    var win = $(window);
     
    var viewport = {
        top  : win.scrollTop(),
        left : win.scrollLeft()
    };

    viewport.bottom = viewport.top + win.height();
     
    var bounds = this.offset();
    bounds.bottom = bounds.top + this.outerHeight();
     
    return !(viewport.bottom < bounds.top || viewport.top > bounds.bottom); 
};

$.fn.scrollStopped = function(callback) {  
    $(this).scroll(function(){
        var self = this, $this = $(self);
        if ($this.data('scrollTimeout')) {
          clearTimeout($this.data('scrollTimeout'));
        }
        $this.data('scrollTimeout', setTimeout(callback, 250, self));
    });
};

var compare_events = function(a,b) {
  if(a.display_order < b.display_order) {
     return -1;
  } else if(a.display_order > b.display_order) {
  	return 1;  	
  }
    
  return 0;
}

var Event = function(obj) {
	this.id            = obj.id;
	this.published     = obj.published;
	this.resource_uri  = obj.resource_uri;
	this.title         = obj.title;
	this.display_order = obj.display_order;
	this.description   = obj.description;
}

var Tag = function(obj) {
	this.id   = obj.id;
	this.name = obj.name;
	this.slug = obj.slug;
}

 var Moment = function(obj) {
	this.caption      = obj.caption;
	this.id           = obj.id;
	this.published    = obj.published;
	this.resource_uri = obj.resource_uri;
	this.rotate_angle = obj.rotate_angle;
	this.data_uri     = obj.data_uri.replace(/\s+/g, '');
	this.event        = obj.event ? new Event(obj.event) : {};
	this.image        = obj.image;
	this.tags         = obj.tags ? obj.tags.map(function(el) { return new Tag(el);}) : {};
}

var Factories = {
	/** Retrieve a list of events. */
	getMoments : function(startIdx, numToGet, callback, error_callback) {
		$.get("/api/v1/moment/?format=json&offset=" + startIdx + "&limit=" + numToGet + "&order_by=event&order_by=id&a=b", function(data) {
			var moments = [];
			for(var obj_key in data.objects) {
				var moment = new Moment(data.objects[obj_key]);
				moments.push(moment);
			}
			
			callback(moments, data.meta.total_count);
		}).fail(function() {
			error_callback();
  		});
	},

	/** Retrieve a map of events keyed by event_id. */
	getEvents : function(callback, error_callback) {
		$.get("/api/v1/event/?format=json&limit=100&order_by=display_order", function(data) {
			var events = {};
			for(var obj_key in data.objects) {
				var ev = new Event(data.objects[obj_key]);
				events[ev.id] = ev;
			}	
			callback(events);
		}).fail(function() {
			error_callback();
  		});
	}
}

var UI = {
	// Data
	events                           : {},
	moments                          : [],
	total_moments                    : 0,      // Total moments that can be retrieved via the API
	current_moment_offset            : 0,      // What is the current moment offset for the API
	current_moment_idx               : 0,      // What is the current selected moment idx

	// Config
	num_moments_to_grab              : 20,     // moments
	infscroll_buffer                 : 300,    // px
	infscroll_lag                    : 300,    // ms
	thumb_width                      : 304,    // px
	large_width                      : 1024,   // px

	// Vars
	is_loading_data                  : false, // Are we currently loading data?
	full_screen                      : false, // Are we in full_screen mode?
	last_scroll_pos                  : 0,     // What is the current scroll offset

	// DOM cache
	event_title                      : null,
	home_title                       : null,
	header_bar                       : null,
	viewport                         : null,
	moment_list_template_html        : "",
	moment_full_screen_template_html : "",
	moment_error_template_html       : "",

	/** Retrieve the next chunk of moments based on the offset and total count/ */
	get_next_moments : function(callback) {
		if(UI.current_moment_offset > UI.total_moments) {
			UI.unlock();
			return;
		}

		var preload_count = 0;
		var preload_max   = 0;

		Factories.getMoments(UI.current_moment_offset, UI.num_moments_to_grab, function(moments, total_moments) {
			UI.total_moments = total_moments;

			if(UI.total_moments <= 0) {
				UI.render_error("No moments found.", "Please use the admin tools to add events and moments.");
				UI.unlock();
				return;
			}

			var x = UI.moments.length;
			var new_moments = [];
			for(var key in moments) {
				var moment = moments[key];
				moment.idx = x++;
				UI.moments.push(moment);
				new_moments.push(moment);
			}

			callback(new_moments);

			UI.current_moment_offset += UI.num_moments_to_grab;
			UI.unlock();
		}, function() {
			UI.render_error("Could not retrieve moments", "Please contact your website admin");
		});
	},

	/** Set the event title i.e. Christmas 2013. */
	set_event_title : function(title) {
		if(title) {
			UI.event_title.html(title);
		} else {
			var events = UI.get_events_on_screen();
			var title  = "";
			for(var i=0; i < events.length; i++) {
				var ev = events[i];
				if(i > 0) {
					title += " / ";
				}

				title += ev.title;
			}

			UI.event_title.html(title);
		}
	},

	/** Return a distinct list of "Event" objects that
	belong to all the moments visible on the screen. */
	get_events_on_screen : function() {
		var event_dict = {};
    	$(".moment").each(function() {
    		var obj = $(this);
    		var ev  = UI.events[obj.attr("event_id")];
    		if(obj.isOnScreen()) {
    			event_dict[ev.id] = ev;
    		}
    	});

    	var events = []; // Sort events by display_order
    	for(var ev_key in event_dict) {
    		events.push(event_dict[ev_key]);
    	}

    	

    	return events.sort(compare_events);
	},

	/** Return the moment indexed by "current_moment_idx".
	Note: current_moment_idx should be set when a moment is clicked/touched. */
	get_current_moment : function() {
		return UI.moments[UI.current_moment_idx];
	},

	render_current_moment : function() {
		UI.lock();
 		var current_moment = UI.get_current_moment(); 
  		var preload = new Image();
  		preload.onload = function() {
	  		UI.render();
	  		UI.set_event_title(current_moment.event.title);
	  		UI.unlock();
  		}
  		preload.src = "/assets/" + current_moment.image + "?width=" + UI.large_width;
	},

	/** Add event handlers to the page. */
	add_handlers : function() {
		UI.set_event_title();
		var clickOrTouch = (('ontouchend' in window)) ? 'touchend' : 'click';

		// Show header in full screen view
		$(window).unbind('mousemove').mousemove(function(ev) {
			if(ev.pageY <= 50) {
				UI.header_bar.slideDown();
			}
		});

		// If the moment caption is clicked then show the header bar
		$("#moment_caption").unbind('click').click(function() {
			UI.header_bar.slideDown();
		});

		// Home button i.e. back to grid view
		UI.home_title.unbind(clickOrTouch).on(clickOrTouch, function(ev) {
			ev.preventDefault();
			if(!UI.full_screen) {
				$("html, body").animate({ scrollTop: "0px" });
			} else {
				UI.lock();
				UI.full_screen = false;
				UI.render();
				UI.unlock();
			}
		});

		var handle_full_screen_nav = function(direction) {
			// Show the header bar when swiping down
			if(direction == 'down') {
				UI.header_bar.slideDown();
				UI.hader_bar_down = true;
  			} else {
  				// Previous moment on swipe right
	  			if(direction == 'right') {
	  				UI.current_moment_idx--;

	  			// Next image on swipe left
	  			} else if(direction == 'left') {
	  				UI.current_moment_idx++;
	  			}

				// Keep image swiping in bounds
	  			if(UI.current_moment_idx < 0) {
	  				UI.current_moment_idx =  0;
	  				UI.render_current_moment();				

	  			// Render the current moment un-altered
	  			} else if(UI.current_moment_idx >= UI.total_moments) {
	  				UI.current_moment_idx = UI.moments.length-1;	  				
	  				UI.render_current_moment();

	  			// Load more moments before advancing the image
	  			} else if(UI.current_moment_idx > UI.moments.length-1) {

	  				UI.get_next_moments(function() {
	  					UI.render_current_moment();
	  				});
	  		    } else {
	  				UI.render_current_moment();
	  			}
	  		}  				
		}

		// Full screen nav swipes
		$("#full_screen").unbind('swipe').swipe({
  			swipe : function(event, direction, distance, duration, fingerCount) {
  				UI.full_screen = true;
  				handle_full_screen_nav(direction);				
  			}
		});		

		$(window).unbind("keyup").one("keyup", function (event) {
			if(!UI.full_screen) {
				return;
			}

			// Handle key navigation
			var direction = "";
			if(event.keyCode == 37) {
				direction = "right";
  			} else if (event.keyCode == 39) {
				direction = "left";
			} else {
				direction = "left";
			}

			if(direction != "") {
				handle_full_screen_nav(direction);
			}
		});
		
		// Click/Touch moment for full screen view
		$(".moment").unbind('click').on('click', function(e) {
			UI.last_scroll_pos    = $(document).scrollTop();
			UI.current_moment_idx = $(this).attr("idx");
			UI.full_screen = true;
			UI.render_current_moment();
		});

		// Change event title i.e. Christmas 2013
		$(window).scrollStopped(function() {
			if(!UI.full_screen) {
				UI.set_event_title();	
			}
		});

		// Infinite scroll
		$(window).scroll(function(e) {
			if(UI.full_screen) {
				return;
			}
    		e.preventDefault();
    		if($(window).scrollTop() >= ($(document).height() - $(window).height() - UI.infscroll_buffer) && !UI.is_locked()) {
				if(UI.current_moment_offset <= UI.total_moments) {
    				UI.lock();
    				setTimeout(function() {
    					UI.get_next_moments(function(new_moments) {
    						UI.render(true, new_moments);
    					});
    				}, UI.infscroll_lag);
    			}
    		}
    	});
	},

	render_error : function(error_text, help_text) {
		UI.viewport.html(Mustache.render(UI.moment_error_template_html, {"error" : error_text, "help" : help_text})).show();
		UI.add_handlers();
	},

	render : function(append, moments) {
		// Full screen render
		if(UI.full_screen) {
			UI.viewport.html(Mustache.render(
				UI.moment_full_screen_template_html , 
				{
					"moment"      : UI.get_current_moment(), 
					"thumb_width" : UI.thumb_width,
					"large_width" : UI.large_width,
					"total_count" : UI.total_moments, 
					"current_idx" : parseInt(UI.current_moment_idx) + 1
				}
			));

			$("#full_screen").fadeIn();
			UI.header_bar.slideUp();
			window.scrollTo(0,0);

		// Grid render
		} else {
			// Append new moments
			if(append && moments) {
				$("#moment_list").append(Mustache.render(
					$("#moment_list_template").html(), 
					{
						"moments"     : moments,
						"thumb_width" : UI.thumb_width,
						"large_width" : UI.large_width
					}
				));
			// Render full list of moments
			} else {
				var moment_html = Mustache.render(
					UI.moment_list_template_html, 
					{
						"moments"     : UI.moments,
						"thumb_width" : UI.thumb_width,
						"large_width" : UI.large_width
					}
				);

				UI.viewport.html('<div id="content"><ul id="moment_list">' + moment_html + '</ul><div class="clear"></div></div>');

				if(UI.last_scroll_pos > 100) {
					setTimeout(function() {
						$("html, body").scrollTop(UI.last_scroll_pos);
					}, 100);					
				}
			}

			// Unhide rendered moments
			$("li:hidden").fadeIn();
		}

		// Add handlers to the UI
		// Note: We need to make sure we unbind events as well
		UI.add_handlers();
	},

	unlock : function() {
		UI.is_loading_data = false;
		$("#loading").fadeOut();
	},

	lock : function() {
		UI.is_loading_data = true;
		$("#loading").show();
	},

	is_locked : function () {
		return UI.is_loading_data;
	},

	init : function() {
		UI.home_title                       = $("#home_title");
		UI.event_title                      = $("#event_title");
		UI.header_bar                       = $("#header_bar");
		UI.viewport                         = $("#viewport");
		UI.moment_list_template_html        = $("#moment_list_template").html();
		UI.moment_full_screen_template_html = $("#moment_full_screen_template").html();
		UI.moment_error_template_html       = $("#error_template").html();

		UI.lock();
		UI.viewport.hide();
		Factories.getEvents(function(events) {
			UI.events = events;
			UI.get_next_moments(function() {
				UI.render();
				UI.viewport.slideDown();
			});
		}, function() {
			UI.render_error("Could not retrieve events", "Please contact your website admin");
		});
	}
}

$(document).ready(function() {	
	UI.init();
});
