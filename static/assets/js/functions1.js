
// $(document).ready(function() {
//     const Toast = Swal.mixin({
//         toast: true,
//         position: "top",
//         showConfirmationButton: false,
//         timer: 2000,
//         timerProgressBar: true,
//     });
//     // Alert - is a "BUILT-IN FUNCTION" to pop- up message in JS
//     function generateCartID() {
//         const ls_cartid = localStorage.getItem("cartID");

//         if (ls_cartid === null) {
//             var cartID = "";

//             for (var i = 0; i < 10; i++) {
//                 cartID += Math.floor(Math.random() * 10);
//             }
//             localStorage.setItem("cartID", cartID);
//         }

//         return ls_cartid || cartID;
//     }


//     // Event listener for "Add to Cart" button clicks   
//     $(document).on("click", ".add_to_cart", function() {
//         const button_el = $(this);  // The clicked button element
//         const id = button_el.data("data-id");
//         const qty = $(".quantity").val();  // Default to 1 if invalid
//         const size = $("input[name='size']:checked").val();
//         const color = $("input[name='color']:checked").val();
//         const cart_id = generateCartID();  // Get or create cart ID

//         $.ajax({
//             url: "/cart/add/" + id + "/",
//             method: "POST",
//             data: {
//                 id:id,
//                 qty: qty,
//                 size: size,
//                 color: color,
//                 cart_id: cart_id,
//                 // csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
//             },

//             beforeSend: function() {
//                 button_el.html("Adding... <i class='fas fa-spinner fa-spin ms-2'></i>");
//             },

//             success: function(response) {
//                 console.log("DEBUG: Add to cart successful", response);
//                 Toast.fire({
//                     icon: "success",
//                     title: response?.message,
//                 });
//                 button_el.html("Add to Cart <i class='fas fa-shopping-cart ms-2'></i>");
//                 $(".total_cart_items").text(response?.total_cart_items);

//             },
                
// });
//     });
// });

