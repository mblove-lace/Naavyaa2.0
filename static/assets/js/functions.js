    // ====================================
    // CART ID GENERATOR 
    // ====================================

// In here, we define a function named generateCartID. 
// This function is responsible for creating a unique cart ID for the user's shopping cart. 
// It first checks if a cart ID already exists in the browser's local storage. 
// If it does, it retrieves and returns that ID. 
// If not, it generates a new 10-digit random number as the cart ID, stores it in local storage, and then returns it. 
// This cart ID is used to identify the user's cart across various operations like adding, updating, or deleting items.
 
function generateCartID() { //Declares a function that creates or retrieves a cart ID. Its is used everywhere cart operations , like add, update, delete are performed.
    // localStorage is a browser API that allows websites to store data locally within the user's browser.
    // getItem is a method of localStorage that retrieves the value associated with a given key.
    let cartID = localStorage.getItem("cartID");
// MAking an if condition to check if cartID exists in local storage. ! means if cartID does not exist.
    if (!cartID) {
        cartID = ""; // Initialize an empty string to build the cart ID.
        for (let i = 0; i < 10; i++) { // Looping it 10 times to create a 10-digit cart ID, by using Math.random() to generate random digits. then appending each digit to cartID.
            cartID += Math.floor(Math.random() * 10);
        }
        localStorage.setItem("cartID", cartID); // Storing the newly generated cart ID in local storage for future use.
        // setItem is a method of localStorage that stores a key-value pair in the browser's local storage.
    }
    return cartID; // Returning the cart ID, whether it was retrieved from local storage or newly generated.
}

// ==================================== DOCUMENT READY FUNCTION  ====================================
// This function ensures that the code inside it / under it runs only after the entire HTML document has been fully loaded and parsed by the browser.

$(document).ready(function () {



    // ================================
    // SWEET ALERT TOAST SETUP
    // ================================

// Here, setting up a SweetAlert2 toast notification configuration, that creates a reusable toast notification style for the application.
// What is SweetAlert2? It is a popular JavaScript library used to create beautiful, customizable alert messages and modal dialogs in web applications.
// mixin is a method provided by SweetAlert2 that defines a set of default options for alerts,but allows for further customization when the alert is actually used.
// Following is the customization options being set for the toast notifications:
    const Toast = Swal.mixin({
        toast: true, // Enables toast-style notifications, which are small, unobtrusive messages that appear temporarily.
        position: "top",
        showConfirmationButton: false, // Disables the confirmation button, making the toast disappear automatically.
        timer: 2000,  
        timerProgressBar: true,
    });

    // ====================================
    // COLOR SELECTION HANDLER
    // ====================================
    let selectedColor = null;

    $(document).on("click", ".color-item", function () {
        $(".color-item").removeClass("active");
        $(this).addClass("active");
        selectedColor = $(this).data("val");
        console.log("Selected Color:", selectedColor);
    });



    // ====================================
    // ADD TO CART HANDLER
    // ====================================

    // This code sets up an event listener for click events on elements with the class add_to_cart.
    // How it works: The page is loaded by document ready function. When a user clicks on an element with the class add_to_cart, the function inside the event listener is triggered.

    // $(document).on("click", ".add_to_cart", function () {
//    ↑         ↑         ↑                ↑
//    |         |         |                |
//  Target   Event    Selector         Function to run

    $(document).on("click", ".add_to_cart", function () {
// This is a debugging statement that logs a message to the console whenever the "Add to Cart" button is clicked.
        console.log("CLICKED on Add to Cart"); 
    // Storing the clicked button element in a variable for later use. 
    // Const is used to declare a variable that cannot be reassigned. And storing the jQuery object representing the clicked button in button_el.
        const button_el = $(this);                                    
        const id = button_el.data("id"); //this gets the product ID from the data-id attribute of the clicked button.
        const qty = $(".quantity-select").val(); // This gets the quantity of the product to be added to the cart from an input field with the class quantity-select.
        const size = $("input[name='option-1']:checked").val(); // This gets the selected size of the product from a group of radio buttons with the name option-1.
        const color = selectedColor; // This gets the selected color of the product from the previously defined selectedColor variable.
        const cart_id = generateCartID(); // This calls the generateCartID function to get the current cart ID.
// Logging or recording the data being sent to the server for debugging purposes. for the developer to see what data is being sent in the AJAX request.
        console.log("Sending → id:", id, "qty:", qty, "size:", size, "color:", color, "cart:", cart_id);

        //  Ajax request to add the product to the cart on the server,i.e the Django backend.
        $.ajax({
            url: "/add_to_cart/", // The URL endpoint on the server where the request is sent.
            method: "POST", // The HTTP method used for the request, which is POST in this case, indicating that data is being sent to the server to create or update a resource.
            data: { // the following data is being sent to the server as part of the request:
                id: id,
                qty: qty,   
                size: size,
                color: color,
                cart_id: cart_id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(), // This includes a CSRF token for security purposes, which is retrieved from a hidden input field in the HTML.
            },
            // Before sending the request, this function is executed to provide user feedback. that is the button text is changed to indicate that the item is being added to the cart.
            beforeSend: function () { 
                button_el.html("Adding to cart <i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },
            // If the request is successful, this function is executed. It logs the server's response, shows a success toast notification, updates the button text back to "Added to Cart", and updates the total cart items displayed on the page.
            success: function (response) {
                console.log("Response:", response);

                Toast.fire({
                    icon: "success",
                    title: response.message,
                });

                button_el.html("Added to Cart <i class='fas fa-shopping-cart ms-2'></i>");
                $(".total_cart_items").text(response.total_cart_items);
            },
            // If there is an error with the request, this function is executed. It console logs the error status and response text, parses the error message from the server's response, and shows an error toast notification with the parsed message.
            // Here, xhr stands for XMLHttpRequest, which is an object that contains information about the error that occurred during the AJAX request.
            error: function (xhr) {
                console.log("Error status:", xhr.status);
                console.log("Response Text:", xhr.responseText);
                // We are parsing the JSON response text from the server to extract the error message. Why? Because the server typically sends error details in JSON format, and we need to convert that JSON string into a JavaScript object to access its properties.
                let errorResponse = JSON.parse(xhr.responseText);
                // Displaying an error toast notification with the error message extracted from the parsed response.
                Toast.fire({
                    icon: "error",
                    title: errorResponse.error,
                });
            }
        });
    });

    // ====================================
    // UPDATE CART HANDLER
    // ====================================


//     $(document).on("click", ".update_cart_qty", function () {

//         const button_el = $(this);

//         const update_type = button_el.attr("data-update-type");
//         const item_id = button_el.attr("data-item-id");
//         const product_id = button_el.attr("data-product-id");
//         var qty = $(".item-qty-" + item_id).val();
//         const cart_id = generateCartID();

//         console.log("=== UPDATE CART CLICKED ===");
//         console.log("Update Type:", update_type);
//         console.log("Item ID:", item_id);
//         console.log("Product ID:", product_id);
//         console.log("Current qty from input:", qty);


// // Getting the current quantity of the item from an input field with a class specific to the item ID. And parsing it as an integer.
    
// // Now, based on the update_type (either "increase" or "decrease"), we adjust the quantity accordingly.
// // Update_type is retrieved from the data-update-type attribute of the clicked button.
//         if (update_type === "increase") {
//             $(".item-qty-" + item_id).val(parseInt(qty) + 1);
//             qty ++;
//         } else {
//             if (parseInt(qty) <= 1) {
//                 $(".item-qty-" + item_id).val(1);
//                 qty = 1;
//             } else {
//                 $(".item-qty-" + item_id).val(parseInt(qty) -1);
//                 qty -- ; // Ensures that the quantity does not go below 1.
//             }
//         }

//         // Updating the input field with the new quantity.

//         $.ajax({
//             url: "/add_to_cart/",
//             method: "POST",
//             data: {
//                 id: product_id,
//                 qty: qty,
//                 cart_id: cart_id,
//                 csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
//             },
//             beforeSend: function (response) {

//                 button_el.html("<i class='fa-solid fa-spinner fa-spin'></i>");
            
//             },  
//             success: function (response) {
//                 Toast.fire({
//                     icon: "success",
//                     title: response.message || "Cart updated",
//                 });
//                 if (update_type === "increase") {
//                     button_el.html("+");
//                 } else {
//                     button_el.html("-");
//                 }
//                 $(".item_sub_total_" + item_id).text(response.item_sub_total); // Updating the item's subtotal display.
//                 $(".cart-sub-total").text("₹ " + response.cart_sub_total);     // Updating the cart's subtotal display.

            
//             },

//             error: function (xhr, status, error) {
//                 console.log(xhr.responseText);
//             }
//         });
//     });

$(document).on("click", ".update_cart_qty", function () {
    console.log("🔴 UPDATE CART CLICKED - Event fired");
    
    const button_el = $(this);
    const update_type = button_el.attr("data-update-type");
    const item_id = button_el.attr("data-item-id");
    const product_id = button_el.attr("data-product-id");
    let qty = parseInt($(".item-qty-" + item_id).val());
    const cart_id = generateCartID();

    console.log("Current qty from input:", qty);
    console.log("Update type:", update_type);

    // Calculate new quantity but DON'T update input field yet
    let newQty;
    if (update_type === "increase") {
        newQty = qty + 1;
    } else {
        newQty = (qty <= 1) ? 1 : qty - 1;
    }
    
    console.log("New qty to send:", newQty);

    $.ajax({
        url: "/add_to_cart/",
        method: "POST",
        data: {
            id: product_id,
            qty: newQty,
            cart_id: cart_id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        beforeSend: function () {
            button_el.html("<i class='fa-solid fa-spinner fa-spin'></i>");
        },  
        success: function (response) {
            console.log("✅ Server response:", response);
            
            Toast.fire({
                icon: "success",
                title: response.message || "Cart updated",
            });
            
            // NOW update the input field (only once, after server confirms)
            $(".item-qty-" + item_id).val(newQty);
            console.log("Updated input to:", newQty);
            
            // Restore button text
            if (update_type === "increase") {
                button_el.html("+");
            } else {
                button_el.html("-");
            }
            
            // Update displayed values
            $(".item_sub_total_" + item_id).text(response.item_sub_total);
            $(".cart-sub-total").text("₹ " + response.cart_sub_total);
        },

        error: function (xhr, status, error) {
            console.log("❌ ERROR:", xhr.responseText);
            // Restore button on error
            if (update_type === "increase") {
                button_el.html("+");
            } else {
                button_el.html("-");
            }
        }
    });
});










    
    // ====================================
    // DELETE CART ITEM HANDLER
    // ====================================
    $(document).on("click", ".delete_cart_item", function () {

        const button_el = $(this);
                
        const item_id = button_el.data("item-id");
        const product_id = button_el.data("product-id");
        const cart_id = generateCartID();
        


        $.ajax({
            url: "/delete_cart_item/",
            method: "POST",
            data: {
                id: product_id,
                item_id: item_id,
                cart_id: cart_id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                Toast.fire({
                    icon: "success",
                    title: response?.message || "Item removed",
                });

                $(".item_div_" + item_id).remove(); // Removing the item's HTML element from the page.
                $(".total_cart_items").text(response.total_cart_items); // Updating the total cart items display.
                $(".cart_sub_total").text(response.cart_sub_total);        // Checking if the cart is now empty after the deletion. If it is, the page is reloaded to reflect the empty cart state.

                if (response.total_cart_items === 0) {
                location.reload();
                }
            }
        });
    });

   

}); // ====================================  END OF DOCUMENT READY FUNCTION   ==================================== //

 // ====================================
    // RAZOR PAY HANDLER
    // ====================================


$(document).on("click", "#rzp-pay-btn", function (e) {
    e.preventDefault();

    const button = $(this);

    // ================================
    // DATA FROM HTML
    // ================================
    const order_id = button.data("order-id");     // Razorpay Order ID from backend and injected into HTML
    const amount = button.data("amount") * 100;  // Razorpay expects  the payment amount to be in paisa, thus *100   
    const email = button.data("email"); // Customer email
    const phone = button.data("phone");    // Customer phone number

    // ================================
    // RAZORPAY OPTIONS
    // ================================
    const options = {
        key: RAZORPAY_KEY_ID,  // Inject from Django template the key id that has been set in settings.py
        amount: amount,
        currency: "INR",
        name: "Your Store Name",
        description: "Order Payment",
        order_id: order_id,   // Razorpay Order ID created in backend
// what is handler here? 
// It is a callback function that is executed when the payment is successfully completed.
        handler: function (response) {
            // ================================
            // PAYMENT SUCCESS CALLBACK
            // ================================

            $.ajax({
                url: `/razorpay_payment_verify/${order_id}/?payment_method=razorpay`,
                method: "POST",
                data: {
                    //In here, we are sending the payment details received from Razorpay to the server for verification. And expecting the server to respond with success or failure. "response."razorpay_payment_id" is the unique identifier for the payment transaction generated by Razorpay.
                    // Here response. is the object received from Razorpay after a successful payment.
                    razorpay_payment_id: response.razorpay_payment_id,
                    razorpay_order_id: response.razorpay_order_id, // This is the same order ID that was used to initiate the payment.
                    razorpay_signature: response.razorpay_signature, // This is a cryptographic signature generated by Razorpay to ensure the authenticity of the payment. Why? Because it helps verify that the payment details have not been tampered with. Why not use the razorpay secret key here? Because secret key should never be exposed on the client side for security reasons.
                    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
                },
                success: function () {
                    window.location.href = `/payment_status/${order_id}/?payment_status=paid`;
                },
                error: function () {
                    window.location.href = `/payment_status/${order_id}/?payment_status=failed`;
                }
            });
        },

        prefill: {
            email: email,
            contact: phone
        },

        theme: {
            color: "#3399cc"
        },

        modal: {
            ondismiss: function () {
                window.location.href = `/payment_status/${order_id}/?payment_status=cancelled`;
            }
        }
    };

    // ================================
    // OPEN RAZORPAY POPUP
    // ================================
    const rzp = new Razorpay(options);
    rzp.open();
});
