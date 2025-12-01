$(document).ready(function () {

    // ================================
    // SWEET ALERT TOAST
    // ================================
    const Toast = Swal.mixin({
        toast: true,
        position: "top",
        showConfirmButton: false,
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
    // CART ID GENERATOR 100% FIXED
    // ====================================
    function generateCartID() {
        let cartID = localStorage.getItem("cartID");

        if (!cartID) {
            cartID = "";
            for (let i = 0; i < 10; i++) {
                cartID += Math.floor(Math.random() * 10);
            }
            localStorage.setItem("cartID", cartID);
        }
        return cartID;
    }

    // ====================================
    // ADD TO CART HANDLER
    // ====================================
    $(document).on("click", ".add_to_cart", function () {

        console.log("CLICK on Add to Cart");

        const button_el = $(this);

        const id = button_el.data("id");
        const qty = $(".quantity-select").val(); // FIXED
        const size = $("input[name='option-1']:checked").val(); // FIXED
        const color = selectedColor; // FIXED
        const cart_id = generateCartID(); // FIXED

        console.log("Sending → id:", id, "qty:", qty, "size:", size, "color:", color, "cart:", cart_id);

        $.ajax({
            url: "/add_to_cart/",
            method: "POST",
            data: {
                id: id,
                qty: qty,
                size: size,
                color: color,
                cart_id: cart_id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },

            beforeSend: function () {
                button_el.html("Adding to cart <i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },

            success: function (response) {
                console.log("Response:", response);

                Toast.fire({
                    icon: "success",
                    title: response.message,
                });

                button_el.html("Add to Cart <i class='fas fa-shopping-cart ms-2'></i>");
                $(".total_cart_items").text(response.total_cart_items);
            },

            error: function (xhr) {
                console.log("Error status:", xhr.status);
                console.log("Response Text:", xhr.responseText);

                let errorResponse = JSON.parse(xhr.responseText);

                Toast.fire({
                    icon: "error",
                    title: errorResponse.error,
                });
            }
        });
    });

});
