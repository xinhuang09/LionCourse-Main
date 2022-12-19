
$(document).ready(function () {
    $("#user_email_nav").html(sessionStorage.getItem('user_email'));
    const all_message  = document.getElementById('all_message');
    
    $('#all_message').append(
        `
        <div>
        ${messages}
        </div>
        `
    )
    display_message();
})


function display_message() {
    $("#all_message").empty();

    $.each(messages, function(index, message) {
        let message_block = display_all_message(message);
        // $("#all_message").append(new_row_email_and_time);
        $("#all_message").append(message_block);
    });
}

function display_all_message(message) {
    var message_block = $("<div></div>")
    message_block.addClass("row")

    var message_content = $("<div></div>");
    message_content.addClass("col-md-7 pl-5");
    message_content.html(message.Content);

    //div for time
    var message_time = $("<div></div>");
    message_time.addClass("col-md-2");
    message_time.html(message.Time);

    //div for email
    var message_email = $("<div></div>");
    message_email.addClass("col-md-3");
    message_email.html(message.Email);

    message_block.append(message_content)
    message_block.append(message_time)
    message_block.append(message_email)

    return message_block;
}