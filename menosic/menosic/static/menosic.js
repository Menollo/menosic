var control_player = local_player;

var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

function play_selected() {
    if (control_player == local_player) {
        var player = $('#player').get(0);
        player.pause();
        $('#player source#mp3').attr('src', $("#playlist .playing a.to_player").attr("mp3"));
        $('#player source#ogg').attr('src', $("#playlist .playing a.to_player").attr("ogg"));
        $('#player').attr('playlist_id', $('#playlist .playing').attr('id'));
        player.load();
        player.play();

        ws.send(JSON.stringify({
            action: "song_change",
            key: key,
            playlist: playlist,
            player: control_player,
            identifier: $('#playlist .playing').attr('id')
        }));
    } else {
        ws.send(JSON.stringify({
            action: "play_song",
            key: key,
            playlist: playlist,
            player: control_player,
            identifier: $('#playlist .playing').attr('id')
        }));
    }
}

function play_next() {
    current = $('#playlist .playing');
    if (current.get(0) != $('#playlist tr:last').get(0)) {
        current.next('tr').addClass('playing');
        current.removeClass('playing');
        play_selected();
    }
}

function link_to_player() {
    $('.playing').removeClass('playing');
    $(this).parent('td').parent('tr').addClass('playing');
    play_selected();
    setTimeout('update_last_played()', 3000)
    return false;
}

function update_playlist(url, notify, async) {
    notify = typeof notify !== 'undefined' ? notify : true;
    async = typeof async !== 'undefined' ? async : true;

    $.ajax({
        url: url,
        async: async,
        success: function(data) {
            if (notify) {
                ws.send(JSON.stringify({
                    action: "update_playlist",
                    key: key,
                    playlist: playlist
                }));
            }
            $("#playlist").html(data);
            if ($("#playlist .playing").length > 0) {
                play_selected();
            } else {
                var playing_id = $('#player').attr('playlist_id')
                $('#playlist #'+playing_id).addClass('playing');
                if($('#playlist .playing').length == 0) {
                    player.pause();
                }
            }
            $('#playlist a.to_playlist').click(link_to_playlist);
            $('#playlist a.to_player').click(link_to_player);
        }
    });
}

function link_to_playlist() {
    var url = $(this).attr('href');
    update_playlist(url)
    return false;
}

function link_to_content() {
    var href = $(this).attr('href');
    $.get(href, function(data) {
        $("#content").html(data);
        $('#content a').click(link_to_content);
        $('#content a.to_playlist').unbind('click').click(link_to_playlist);
    });
    return false;
}

function update_last_played() {
    $.get('/last_played/', function(data) {
        $('#last_played').html(data);
        $('#meta a.to_content').click(link_to_content);
    });
}

function append_results(div, name, title, data) {
    div.append('<h4>' + title + '</h4>');
    div.append('<ul class="' + name + '" />');
    $(data).each(function(id, item) {
        if (name == 'artists') {
            var display = item['name'];
        } else {
            var display = item['artist'] + ' - ' + item['title'];
        }
        var link = $("<a href='"+ item['url'] +"'>" + display + "</a>");
        link.click(link_to_content);
        div.find('ul.' + name).append($("<li>").append(link));
    });

}

var last_search_keystroke = Date.now();
function search(term) {
    last_search_keystroke = Date.now();
    if (term.length > 2) {
        $.getJSON(search_url, {'q': term}, function(data) {
            $('#content-meta #search-results').remove();
            $('#meta').hide();
            $('#content-meta').append('<div id="search-results" class="extra" />');
            var results = $('#content-meta #search-results');
            results.append('<h3 class="glyphicon glyphicon-search">Results</h3>');

            append_results(results, 'artists', 'Artists', data['artists']);
            append_results(results, 'albums', 'Albums', data['albums']);
            append_results(results, 'tracks', 'Tracks', data['tracks']);
        });
    } else {
        $('#content-meta #search-results').remove();
        $('#meta').show();
    }
}

function search_delay() {
	term = this.value;
	delay(function() {
		search(term);
	}, 300);
}

function change_players() {
    control_player = $(this).val();
    if (control_player == local_player) {
        $('#player').show();
        $('#client-control').hide();
    } else {
        $('#player').hide();
        $('#client-control').css('display', 'flex');
    }
}

$(document).ready(function() {
    $('#left-content a, #navigation a.external, a.to_content, #content a').click(link_to_content);
    $('#playlist a.to_player').click(link_to_player);
    $('#playlist a.to_playlist').click(link_to_playlist);
    $('#player').bind('ended', play_next);
    $('#searchbox').bind('keyup', search_delay);
    $('#searchbox').bind('focus', function() {
        // clear search field on focus after 10 sec..
        if ((Date.now() - last_search_keystroke) > 10000) {
            $(this).val('');
        }
    });
    $('#players').bind('change', change_players);
    $("#players").append('<option value="' + player + '">' + control_player + '</option>');
    setInterval(update_last_played, 30000);
    update_last_played();

    $('#left-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    })

    ws = new WebSocket(ws_url);

    ws.onmessage = function(message) {
        var obj = JSON.parse(message.data);

        if (obj['action'] == 'players') {
            $("#players").empty();
            $.each(obj['players'], function(index, item) {
                var selected = '';
                if (item['player'] == control_player) {
                    selected = 'selected';
                }

                var name = item['name']
                if (item['player'] == local_player) {
                    name = name + " (this)";
                } else {
                    name = name + " ("+item['player']+")";
                }
                $("#players").append('<option '+ selected +' value="' + item['player'] + '">' + name + '</option>');
            });
        } else if(obj['action'] == 'update_playlist') {
            if (obj['playlist'] == playlist) {
                update_playlist(playlist_url, false, false);
            }
        } else if(obj['action'] == 'song_change') {
            if (obj['playlist'] == playlist && obj['player'] == control_player) {
                $('#playlist tr').removeClass('playing');
                $('#playlist #' + obj['identifier']).addClass('playing');
            }
        } else if(obj['action'] == 'pause') {
            if (obj['player'] == control_player) {
                var player = $('#player').get(0);
                if (player.paused) {
                    player.play();
                } else {
                    player.pause();
                }
            }
        } else if(obj['action'] == 'next') {
            if (obj['player'] == control_player) {
                play_next();
            }
        } else if(obj['action'] == 'play_song') {
            if (obj['playlist'] == playlist && obj['player'] == control_player) {
                $('#playlist tr').removeClass('playing');
                $('#playlist #' + obj['identifier']).addClass('playing');
                play_selected();
            }
        } else {
            console.log(obj);
        }

    }
    ws.onopen = function() {
        ws.send(JSON.stringify({
            action: "register",
            key: key,
            player: local_player,
            playlist: playlist,
            name: 'Browser'
        }));
    }

    // client control
    $("#client_pause").click(function() {
        ws.send(JSON.stringify({
            action: "pause",
            key: key,
            player: control_player,
        }));

    });
    $("#client_next").click(function() {
        ws.send(JSON.stringify({
            action: "next",
            key: key,
            player: control_player,
        }));
    });
});
