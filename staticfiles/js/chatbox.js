const logged_in_user = JSON.parse(
  document.getElementById("logged_in_user").textContent
);
var s_key;

//for encryption and decryption
const XOREncryptDecrypt = (message, keyString) => {
  const key = keyString.split("");
  const output = [];
  for (let i = 0; i < message.length; i++) {
    const charCode = message.charCodeAt(i) ^ key[i % key.length].charCodeAt(0);
    output.push(String.fromCharCode(charCode));
  }
  return output.join("");
};

const encrypt = (message, key) => XOREncryptDecrypt(message, key);

const decrypt = (encryptedMessage, key) =>
  XOREncryptDecrypt(encryptedMessage, key);

function getChatMessages(user_2) {
  $.ajax({
    url: "get_messages/",
    type: "GET",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
    data: {
      user_2: user_2,
    },
    success: (data) => {
      $(".msg-body ul").children().hide();
      $(".msg-body ul").html(data);
      console.log("Chat fetched.");
      document
        .querySelector(".msg-body")
        .scrollIntoView({ behavior: "smooth", block: "end" });
    },
    error: (error) => {
      console.log(error);
    },
  });
}

function getSharedKey(p_key) {
  console.log("here");
  $.ajax({
    url: "get_shared_key/",
    type: "GET",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
    data: {
      p_key: p_key,
    },
    success: (data) => {
      console.log("secret_key_fetched");
      s_key = data["s_key"];
    },
    error: (error) => {
      console.log(error);
    },
  });
}

// Messaging

function setUserDetail() {
  var userName = $(".selected .connection--name").text();
  var userImage = $(".selected .connection--image").attr("src");

  $(".user--name").text(userName);
  $(".user--image").attr("src", userImage);
}

function appendMessages(data) {
  var list = document.createElement("li");
  var para = document.createElement("p");
  var chat_span = document.createElement("span");
  chat_span.className = "time";
  chat_span.innerText = data.timestamp;
  para.innerText = decrypt(data.message, s_key);
  list.appendChild(para);
  list.appendChild(chat_span);
  if (data.sent_by == logged_in_user.id) {
    list.className = "repaly";
  } else {
    list.className = "sender";
  }
  if (
    $(".selected").attr("data-userId") == data.sent_by ||
    $(".selected").attr("data-userId") == data.sent_to
  ) {
    $(".chat--messages").append(list);
  }
  document
    .querySelector(".msg-body")
    .scrollIntoView({ behavior: "smooth", block: "end" });
}

function showTypingAnimation(data) {
  if ($(".selected").attr("data-userId") === data.sent_by) {
    $(".msg-body > .typing").show();
    var clearInterval = 900;
    var clearTimerId;

    clearTimeout(clearTimerId);
    clearTimerId = setTimeout(function () {
      $(".typing").hide();
    }, clearInterval);
    document
      .querySelector(".msg-body")
      .scrollIntoView({ behavior: "smooth", block: "end" });
  } else {
    $(".connection[data-userId=" + data.sent_by + "] > .typing").show();
    var clearInterval = 900;
    var clearTimerId;

    clearTimeout(clearTimerId);
    clearTimerId = setTimeout(function () {
      $(".connection[data-userId=" + data.sent_by + "] > .typing").hide();
    }, clearInterval);
  }
}

jQuery(document).ready(function () {
  $(".chat-list a").click(function () {
    $(".chatbox").addClass("showbox");
    return false;
  });

  $(".chat-icon").click(function () {
    $(".chatbox").removeClass("showbox");
  });

  $(".connection:first").addClass("selected");
  $(".typing").hide();

  var userId = $(".connection:first").attr("data-userId");
  getChatMessages(userId);
  setUserDetail();
  var nextURL = window.location.origin + "/chat/?u_id=" + userId;
  var nextTitle = "My new page title";
  var nextState = { additionalInformation: "Updated the URL with JS" };
  window.history.replaceState(nextState, nextTitle, nextURL);
  setUpWebSocket(userId);
});

$(".connection").click(function () {
  $(".selected").removeClass("selected");
  $(this).addClass("selected");
  var userId = $(this).attr("data-userId");

  getChatMessages(userId);
  setUserDetail();

  var nextURL = window.location.origin + "/chat/?u_id=" + userId;
  var nextTitle = "My new page title";
  var nextState = { additionalInformation: "Updated the URL with JS" };
  window.history.replaceState(nextState, nextTitle, nextURL);
  setUpWebSocket(userId);
});

var chatSocket = null;

function closeWebSocket() {
  if (chatSocket != null) {
    chatSocket.close();
    console.log("Socket closed");
    chatSocket = null;
  }
}

function setUpWebSocket(userId) {
  closeWebSocket();
  chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + userId + "/"
  );

  chatSocket.onopen = function (e) {
    console.log("New socket opened");
  };

  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.p_key) {
      p_key = data.p_key;
      getSharedKey(p_key);
    } else if (data.command === "is_typing") {
      showTypingAnimation(data);
    } else if (data.command === "delete_conversation") {
      getChatMessages($(".selected").attr("data-userId"));
    } else {
      appendMessages(data);
    }
  };

  chatSocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
  };

  document.querySelector("#chat-message-input").focus();
  $("#chat-message-input").keyup(function () {
    chatSocket.send(
      JSON.stringify({
        type: "chat_message",
        command: "is_typing",
        sent_by: logged_in_user["id"],
        sent_to: $(".selected").attr("data-userId"),
      })
    );
  });

  document.querySelector("#chat-message-submit").onclick = function (e) {
    e.preventDefault();
    const messageInputDom = document.querySelector("#chat-message-input");
    const message = messageInputDom.value;
    if (message.length != 0) {
      chatSocket.send(
        JSON.stringify({
          type: "chat_message",
          command: "private_chat",
          message: encrypt(message, s_key),
          sent_by: logged_in_user["id"],
          sent_to: $(".selected").attr("data-userId"),
        })
      );
      messageInputDom.value = "";
    }
  };
}

$("#deleteConversation").click(function () {
  $.ajax({
    url: "delete_chat/",
    type: "DELETE",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    data: JSON.stringify({
      connection: $(".selected").attr("data-userId"),
    }),
    success: (data) => {
      triggerAlert(data["status"], "success");
      chatSocket.send(
        JSON.stringify({
          type: "chat_message",
          command: "delete_conversation",
          sent_by: logged_in_user["id"],
          sent_to: $(".selected").attr("data-userId"),
        })
      );
    },
    error: (error) => {
      console.log(error);
    },
  });
});

function blockUser() {
  $.ajax({
    url: "block_user/",
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    data: {
      target_user_id: $(".selected").attr("data-userId"),
    },
    success: (data) => {
      location.reload(true);
      // triggerAlert(data["status"], 'success');
    },
    error: (error) => {
      console.log(error);
    },
  });
}
