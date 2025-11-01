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
    // FUNCTION: Generate or retrieve a unique cart ID from localStorage : CartID Generator function
       // -------------------------------

    //    Creates or retrieves a unique identifier for the user's cart session.
    function generateCartID() {
          // Check if a cart ID already exists in localStorage
        const ls_cartid = localStorage.getItem("cartID");
          // If there’s no cart ID in localStorage, create a new one
        if(ls_cartid === null) {
            var cartID = "";

            // Create an empty string to hold the cart ID 
 // Generate a random 10-digit number as a unique ID
 // for (var i = 0; i < 10; i++): Loop that runs 10 times:  generates random decimal between 0 and 10
 // Math.floor()- Rounds down to get integer (0-9) and += → appends to cartID string



        for (var i = 0; i < 10; i++) {
            cartID += Math.floor(Math.random() * 10);
        }
// Saves the new cart ID to localStorage so it persists across page reloads.
        localStorage.setItem("cartID",cartID);

        return cartID;
    }
//  If a cart ID already exists, return that existing ID
    return ls_cartid;

}



    // -------------------------------    // ADD TO CART FUNCTIONALITY    // -------------------------------


// $ - Jquery shortcut- When you call $() with something inside the parentheses, it returns a jQuery object 
// It’s a variable name that happens to hold the main jQuery function.

//  Here, document is the loaded HTML website- treated as an object  which will go through jqerry library 
//  Clicker function is attached and it will find .add_to_cart DOM portion in the product.html
// When that element is clicked, the function inside will run.

//So, in short,listens for clicks on ANY element with class add_to_cart (event delegation - works even for dynamically added buttons).
    $(document).on("click", ".add_to_cart", function(){
        // $(this) refers to the specific button that was clicked. Wrapped in $() to make it a jQuery object.
        // button_el is a jQuery object representing the clicked button. Use it to change text, disable, etc.
        // button_el is a jQuery object representing the clicked button. Use it to change text, disable, etc.
        const button_el = $(this)
        
        // Reads the HTML attribute data-id from the button. Typical HTML: <button class="add_to_cart" data-id="5">Add</button>.
        // Useful to send the product id to the server.
        const id = button_el.attr("data-id")
        // Reads the value of the element with id="quantity". Typically an <input> field where users enter quantity.
        const qty = $("#quantity").val()
        // These find checked radio inputs with name size and color. They take the currently selected value.
        const size = $("input[name='size']:checked").val();
        const color = $("input[name='color']:checked").val();
        // Calls a custom JS function (not shown) that should return a unique cart identifier (string). Maybe stored in cookie/session afterwards.
        // Implementation detail: generateCartID() must be idempotent per user session (or else multiple different cart IDs will be created). Usually you generate once and save to session/localStorage.
        const cart_id = generateCartID()


        // Sends an AJAX GET request to the server at /add_to_cart/ with product details.
        // On success or error, updates the button text and shows a toast notification.
        $.ajax({
            // The endpoint to hit on your server (relative path). In Django you'd have a URL pattern like path('add_to_cart/', views.add_to_cart).
            url: "/add_to_cart/",
            // the data being sent to the server
            method: "POST",
            data: {
                id: id,
                qty: qty,
                size:size,
                color: color,
                cart_id: cart_id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
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