console.log("function.js loaded");
<button class="add_to_cart" data-id="{{ product.id }}">Add to cart</button>

$(document).ready(function () {
    const Toast = Swal.mixin({
        toast: true,
        position: "top",
        showConfirmationButton: false,
        timer:2000,
        timerProgressBar:true,
    })
    function generateCartID() {
        const ls_cartid = localStorage.getItem("cartID");

        if(ls_cartid === null) {
            var cartID = "";

            for (var i = 0; i < 10; i++) {
                cartID += Math.floor(Math.random() * 10);
            }

            localStorage.setItem("cartId",cartID);
        }

        return ls_cartid || cartID
    }

    $(document).on("click",".add_to_cart", function(){
        const button_el = $(this)
    })


    $(document).on("click", ".add_to_cart", function(){

        const button_el = $(this)
        const id = butoon_el.attr("data-id")
        const qty = $(".quantity").val()
        const size = $ ("input[name='size]:checked").val();
        const color = $ ("input[name='color]:checked").val();
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
                button_el.html("Adding to cart <i class= 'fas fa-spinner fa-spin ms-2> <>");
            },
            success: function(response){
                console.log (response);
                Toast.fire({
                    icon:"success",
                    title: response?.message,
                });
                button_el.html ("Add to Cart <i class='fas fa-spinner fa-shopping-cart ms-2> <>");
                $(".total_cart_items").text(response?.total_cart_items);
            },


            error: function(xhr,status,error){
                console.log("Error status:", xhr.status);
                console.log("Response Text:" , xhr.responseText);

                let errorResponse = JSON.parse(xhr.responseText)
                Toast.fire({
                    icon:"success",
                    title: erroResponse?.error,
                });
            }
              
        });
    })

});



// // <!-- example button in template (inside loop for product) -->
// <button class="add_to_cart" data-id="{{ product.id }}">Add to cart</button>


// $(document).ready(function () {
//     const Toast = Swal.mixin({
//         toast: true,
//         position: "top",
//         showConfirmButton: false,
//         timer: 2000,
//         timerProgressBar: true,
//     });

//     function generateCartID() {
//         const KEY = "cartID";                 // consistent key
//         let ls_cartid = localStorage.getItem(KEY);

//         if (!ls_cartid) {
//             let cartID = "";
//             for (let i = 0; i < 10; i++) {
//                 cartID += Math.floor(Math.random() * 10);
//             }
//             localStorage.setItem(KEY, cartID);
//             ls_cartid = cartID;
//         }

//         return ls_cartid;
//     }

//     // jQuery global AJAX setup to send CSRF token with POST
//     function getCookie(name) {
//         const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
//         return match ? match.pop() : '';
//     }
//     const csrftoken = getCookie('csrftoken');

//     $.ajaxSetup({
//         beforeSend: function(xhr, settings) {
//             if (!(/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type))) {
//                 xhr.setRequestHeader("X-CSRFToken", csrftoken);
//             }
//         }
//     });

//     $(document).on("click", ".add_to_cart", function (e) {
//         e.preventDefault();

//         const button_el = $(this);
//         const id = button_el.attr("data-id");
//         const qty = $(".quantity").val() || 1;
//         const size = $("input[name='size']:checked").val() || null;
//         const color = $("input[name='color']:checked").val() || null;
//         const cart_id = generateCartID();

//         $.ajax({
//             url: "/add_to_cart/",
//             method: "POST",
//             contentType: "application/json",
//             data: JSON.stringify({
//                 id: id,
//                 qty: qty,
//                 size: size,
//                 color: color,
//                 cart_id: cart_id,
//             }),
//             beforeSend: function(){
//                 button_el.prop('disabled', true);
//                 button_el.html("Adding to cart <i class='fas fa-spinner fa-spin ms-2'></i>");
//             },
//             success: function(response){
//                 Toast.fire({
//                     icon: "success",
//                     title: response?.message || "Added to cart",
//                 });
//                 button_el.html("Add to cart <i class='fas fa-shopping-cart ms-2'></i>");
//                 button_el.prop('disabled', false);

//                 if (response?.total_cart_items !== undefined) {
//                     $(".total_cart_items").text(response.total_cart_items);
//                 }
//             },
//             error: function(xhr){
//                 console.error("Add to cart failed:", xhr);
//                 Toast.fire({
//                     icon: "error",
//                     title: "Could not add to cart",
//                 });
//                 button_el.prop('disabled', false);
//                 button_el.html("Add to cart <i class='fas fa-shopping-cart ms-2'></i>");
//             }
//         });
//     });
// });

