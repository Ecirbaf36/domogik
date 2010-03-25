const close_without_change = 10000; // 10 seconds
const close_with_change = 3000; // 3 seconds

(function($) {
	$.widget("ui.range_command", {
        _init: function() {
            var self = this, o = this.options;
			var states = o.states.toLowerCase().split(/\s*,\s*/);
			this.min_value = states[0];
			this.max_value = states[1];
			this.steps = states[2];
            this.widgets = new Array();
            this.element.addClass('command_range')
                .addClass('icon32-state-' + o.usage);
			this.name = this.element.find('.name').text();
			var ul = $("<ul></ul>");
            var limin = $("<li></li>");
            var amin = $("<button class='buttontext capitalletter'>Min</button>");
            amin.click(function() {
                    self.min_range();
					self.processValue();
                });
            var limax = $("<li></li>");
            var amax = $("<button class='buttontext capitalletter'>Max</button>");
            amax.click(function() {
                    self.max_range();
					self.processValue();
                });
            limin.append(amin);
            limax.append(amax);
            ul.append(limin);
            ul.append(limax);
            this.element.append(ul);
			var id = this.element.attr('id');
			var divValue = $("<div class='ui-slider-value'/>");
			divValue.append("<label id='" + id + "_label' for='" + id + "_input'>Dim:</label>");
			this.sliderInput = $("<input id='" + id + "_input' type='text' maxlength='3' class='ui-slider-input' />");
			divValue.append(this.sliderInput);
			this.element.append(divValue);	
			this.slider = $("<div id='" + id + "_slider'></div>");
			this.element.append(this.slider);

			this.slider.slider({
				range: "min",
				min: this.min_value,
				max: this.max_value,
//bug				step: this.steps,
				slide: function(event, ui) {
					self.setProcessingValue(ui.value);
				},
				stop: function(event, ui) {
					self.resetAutoClose();
				}

			});
        },
                
        registerWidget: function(id) {
            this.widgets.push(id);
            $(id).range_widget({
                command: this,
                usage: this.options.usage,
				min_value: this.min_value,
				max_value: this.max_value,
				steps: this.steps,
				unit: this.options.unit
            })
			.range_widget('displayValue', this.currentValue, this.currentIcon, null);
        },
		
		setValue: function(value) {
			var self = this;
			if (value >= this.min_value && value <= this.max_value) {
				this.currentValue = value;
			} else if (value < this.min_value) {
				this.currentValue = this.min_value;
			} else if (value > this.max_value) {
				this.currentValue = this.max_value
			}
			this.processingValue = this.currentValue;
			var percent = (this.currentValue / (this.max_value - this.min_value)) * 100;
			var icon = 'range_' + findRangeIcon(this.options.usage, percent);

            this.displayValue(this.currentValue, icon, this.currentIcon);
			$.each(this.widgets, function(index, value) {
                $(value).range_widget('displayValue', self.currentValue, icon, this.currentIcon);
            });
			this.currentIcon = icon;
        },

		setProcessingValue: function(value) {
			var self = this;
			if (value >= this.min_value && value <= this.max_value) {
				this.processingValue = value;
			} else if (value < this.min_value) {
				this.processingValue = this.min_value;
			} else if (value > this.max_value) {
				this.processingValue = this.max_value
			}
			var percent = (this.processingValue / (this.max_value - this.min_value)) * 100;

            this.displayProcessingValue(this.processingValue, percent);
			$.each(this.widgets, function(index, value) {
                $(value).range_widget('displayProcessingValue', self.processingValue, percent);
            });
		},
		
		processValue: function() {
			if (this.processingValue != this.currentValue) { // If the value was changed
				this.options.action(this, this.processingValue);				
			}
		},
		
		displayRangeIcon: function(newIcon, previousIcon) {
			if (previousIcon) {
				this.element.removeClass(previousIcon);				
			}
			this.element.addClass(newIcon);
        },
		
        displayValue: function(value, newIcon, previousIcon) {
			var self = this, o = this.options;
            this.displayRangeIcon(newIcon, previousIcon);
			this.element.find('.name').text(this.name + ' - ' + value + o.unit)
			if (this.slider.slider( "option", "value") != value ) {
				this.slider.slider( "option", "value", value );				
			}
        },
		
        displayProcessingValue: function(value, percent) {
			this.sliderInput.val(value);
			if (this.slider.slider( "option", "value") != value ) {
				this.slider.slider( "option", "value", value );				
			}
        },
		
		plus_range: function() {
			var value = Math.floor((this.processingValue + this.steps) / this.steps) * this.steps;
			this.setProcessingValue(value);
		},
		
		minus_range: function() {
			var value = Math.floor((this.processingValue - this.steps) / this.steps) * this.steps;
			this.setProcessingValue(value);
		},
		
		max_range: function() {
			this.setProcessingValue(this.max_value);
		},
		
		min_range: function() {
			this.setProcessingValue(this.min_value);
		},
		
		resetAutoClose: function() {
			var self = this;
			this.element.doTimeout( 'timeout', close_with_change, function(){
				$.each(self.widgets, function(index, value) {
					$(value).range_widget('close');
				});
				self.processValue();
			});	
		}
		
	});
    
    $.extend($.ui.range_command, {
        defaults: {
        }
    });
	
	/* Widget */
    
    $.widget("ui.range_widget_core", {
        _init: function() {
            var self = this, o = this.options;
            this.element.addClass('widget_range')
                .attr("tabindex", 0);
			this.elementstate = $("<div class='widget_state'></div>");
            this.elementicon = $("<div class='widget_icon'></div>");
			this.elementvalue = $("<div class='widget_value'></div>");
            if(o.isCommand) {
                this.elementvalue.addClass('icon32-usage-' + o.usage);                
            } else {
                this.elementvalue.addClass('icon32-state-' + o.usage);                
            }
			this.element.append(this.elementstate);
			this.elementicon.append(this.elementvalue);				
            this.element.append(this.elementicon);
			this.displayBackground(0);
        },

		displayBackground: function(percent) {
			this.elementicon.css('-moz-background-size', '100% ' + percent + '%');
			this.elementicon.css('-webkit-background-size', '100% ' + percent + '%');
        },

		displayRangeIcon: function(newIcon, previousIcon) {
			if (previousIcon) {
				this.elementvalue.removeClass(previousIcon);				
			}
			this.elementvalue.addClass(newIcon);
        },
		
		displayValue: function(value, unit) {
			this.elementstate.text(value + unit);
			this.elementvalue.text('');
			this.elementicon.css('-moz-background-size', '0');
			this.elementicon.css('-webkit-background-size', '0');
        },
		
		displayProcessingValue: function(value, unit) {
			this.elementvalue.text(value + unit);
		}
    });
    
    $.extend($.ui.range_widget_core, {
        defaults: {
			isCommand: false
        }
    });
    
    $.widget("ui.range_widget", {
        _init: function() {
            var self = this, o = this.options;
            this.element.range_widget_core({
                usage: o.usage
            });
			this.button_plus = $("<div class='range_plus' style='display:none'></div>");
			this.button_plus.click(function (e) {self.plus();e.stopPropagation()});
			this.button_minus = $("<div class='range_minus' style='display:none'></div>");
			this.button_minus.click(function (e) {self.minus();e.stopPropagation()});
			this.button_max = $("<div class='range_max' style='display:none'></div>");
			this.button_max.click(function (e) {self.max();e.stopPropagation()});
			this.button_min = $("<div class='range_min' style='display:none'></div>");
			this.button_min.click(function (e) {self.min();e.stopPropagation()});
			this.element.addClass('closed');
			this.element.find('.widget_icon').append(this.button_plus)
				.append(this.button_minus)
				.append(this.button_max)
				.append(this.button_min)
				.click(function (e) {
						if (self.openflag) {
							self.close();
							self.options.command.processValue();							
						} else {
							self.open();							
						}
						e.stopPropagation();
					});
			this.element.keypress(function (e) {
					switch(e.keyCode) { 
					// User pressed "home" key
					case 36:
						self.max();
						break;
					// User pressed "end" key
					case 35:
						self.min();
						break;
					// User pressed "up" arrow
					case 38:
						self.plus();
						break;
					// User pressed "down" arrow
					case 40:
						self.minus();
						break;
					}
					e.stopPropagation();
				});
        },
		
		displayValue: function(value, newIcon, previousIcon) {
            this.element.range_widget_core('displayRangeIcon', newIcon, previousIcon);                
            this.element.range_widget_core('displayValue', value, this.options.unit);                
        },

		displayProcessingValue: function(value, percent) {
            this.element.range_widget_core('displayBackground', percent);
            this.element.range_widget_core('displayProcessingValue', value, this.options.unit);                
        },
		
		plus: function() {
			this.options.command.resetAutoClose();
			this.options.command.plus_range();
		},

		minus: function() {
			this.options.command.resetAutoClose();
			this.options.command.minus_range();
		},
		
		max: function() {
			this.options.command.resetAutoClose();
			this.options.command.max_range();
		},
		
		min: function() {
			this.options.command.resetAutoClose();
			this.options.command.min_range();
		},
		
		open: function() {
			var self = this;
			this.openflag = true;
			this.element.removeClass('closed')
				.addClass('opened');
			this.button_plus.show();
			this.button_minus.show();
			this.button_max.show();
			this.button_min.show();
			this.displayProcessingValue(this.options.command.currentValue);
			this.element.doTimeout( 'timeout', close_without_change, function(){
				self.close();
			});
		},
		
		close: function() {
			this.openflag = false;
			this.element.removeClass('opened')
				.addClass('closed');
			this.button_plus.hide();
			this.button_minus.hide();
			this.button_max.hide();
			this.button_min.hide();
		}
    });
	
    $.extend($.ui.range_widget, {
        defaults: {
        }
    });
})(jQuery);