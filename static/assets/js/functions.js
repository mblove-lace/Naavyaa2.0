// CSS class used as a selector for the click event and 
// Custom data attribute storing the product ID (template syntax suggests Django/Jinja2)
// When the page loads, the template engine (Django/Jinja2) processes {{ product.id }} and replaces it with an actual product ID
// and triggers the click event 

/* <button class="add_to_cart" data-id="{{ product.id }}">Add to cart </button> */

//  Ensures the code runs only after the DOM-() document object model - tree like representation of the entire HTML page, that browsers create when loading a webpage.)  is fully loaded

//  What does it mean ? - 
//    When your browser loads a webpage, it goes through a few steps:
// 1.Downloads the HTML file from the server.

//  2. Reads it line by line and creates a DOM (Document Object Model) — a tree-like structure representing every HTML tag as a JavaScript object in memory.
// 3.Once that tree (DOM) is ready, JavaScript can safely find and modify elements —
// for example, document.querySelector('button') will work because the <button> now exists in memory.
// After that, ensures the jQuery-dependent initialization runs when the document is ready.
$(document).ready(function () {
    // Alert - is a "BUILT-IN FUNCTION" to pop- up message in JS 
    // Configured SweetAlert2(a JavaScript library that lets you show  customizable alert popups) instance for displaying notifications
    // using SweetAlert2 and configuring it to behave like a toast.
    const Toast = Swal.mixin({
        // Enables toast-style (small, non-intrusive) alerts at the top of the screen
        toast: true, 
        position: "top",
        // Hides the OK button 
        showConfirmationButton: false,
        timer:2000,  //Popup will close automatically after 2 seconds
        timerProgressBar: true,  // Show a progress bar while the timer runs
    })

        // -------------------------------
    // FUNCTION: Generate or retrieve a unique cart ID from localStorage
    // -------------------------------

    function generateCartID() {
          // Check if a cart ID already exists in localStorage
        const ls_cartid = localStorage.getItem("cartID");
          // If there’s no cart ID in localStorage, create a new one
        if(ls_cartid === null) {
            var cartID = "";

            
 // Generate a random 10-digit number as a unique ID
 // for (var i = 0; i < 10; i++): Loop that runs 10 times:  generates random decimal between 0 and 10
 // Rounds down to get integer (0-9)

        for (var i = 0; i < 10; i++) {
            cartID += Math.floor(Math.random() * 10);
        }

        localStorage.setItem("cartID",cartID);
    }

        return ls_cartid || cartID
    }
// $ - Jquery shortcut- When you call $() with something inside the parentheses, it returns a jQuery object 
// It’s a variable name that happens to hold the main jQuery function.

//  Here, document is the loaded HTML website- treated as an object  which will go through jqerry library 
//  Clicker function is attached and it will find .add_to_cart DOM portion in the product.html
    $(document).on("click", ".add_to_cart", function(){
        
        const button_el = $(this)
        const id = button_el.attr("data-id")
        const qty = $("#quantity").val()
        const size = $("input[name='size']:checked").val();
        const color = $("input[name='color']:checked").val();
        const cart_id = generateCartID()

        $.ajax({
            url: "/add_to_cart/",
            data: {
                id: id,
                qty: qty,
                size:size,
                color: color,
                cart_id: cart_id,
            },
            beforeSend: function(){
                button_el.html("Adding to cart <i class='fas fa-spinner fa-spin ms-2'> </i>");
            },
            success: function(response){
                console.log (response);
                Toast.fire({
                    icon:"success",
                    title: response?.message,
                });
                button_el.html ("Add to Cart <i class='fas fa-shopping-cart ms-2'> </i>");
                $(".total_cart_items").text(response?.total_cart_items);
            },


            error: function(xhr,status,error){
                console.log("Error status:", xhr.status);
                console.log("Response Text:" , xhr.responseText);

                let errorResponse = JSON.parse(xhr.responseText)
                Toast.fire({
                    icon:"error",
                    title: errorResponse?.error,
                });
            }
              
        });
    })

});