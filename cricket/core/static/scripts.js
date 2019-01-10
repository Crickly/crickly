function resultsSearch(){
  year = $('#yearSelect').val();
  month = $('#monthSelect').val();
  $.getJSON('/api/results/' + year + '/' + month + '/', function(data){
    if (data.error){
      alert('There was an issue getting the matches!')
    }else{
      data = data.data;
      $('#match-table tbody').empty()
      if (data.matches.length != 0){
        $('#matches-error-message').css('display', 'none');
        $.each(data.matches, function(i, item){
          var $tr = $('<tr>').append(
            $('<td>').html(item.match_date),
            $('<td>').html(item.home_club_name + '<br>' + item.home_team_name),
            $('<td>').html(item.away_club_name + '<br>' + item.away_team_name),
            $('<td>').html(item.result_description),
            $('<td>').html('<a href="/matches/' + item.id + '/">Link</a></td>')
          ).appendTo('#match-table tbody');
        });
      }else{
        $('#matches-error-message').css('display', 'block')
      };
    };
  });
};

function fixtureSearch(){
  period = $('#periodSelect').val();
  $.getJSON('/api/fixtures/' + period + '/', function(data){
    if (data.error){
      if (data.message != ''){
        alert(data.message)
      }else{
        alert('There was an issue getting the fixtures');
      }
    }else{
      requestData = data.data;
      $('#match-table tbody').empty()
      if (requestData.matches.length != 0){
        $('#mathes-error-messgae').css('display', 'none');
        $.each(requestData.matches, function(i, item){
          $('<tr>').append(
            $('<td>').html(item.match_date),
            $('<td>').html(item.home_club_name + '<br>' + item.home_team_name),
            $('<td>').html(item.away_club_name + '<br>' + item.away_team_name),
            $('<td>').html('<a href="/matches/' + item.id + '/">Link</a></td>')
          ).appendTo('#match-table tbody');
        });
      }else{
        $('#matches-error-message').css('display', 'block');
      }
    };
  });
};

function battingStatsSearch(){
  year = $('#yearSelect').val();
  team = $('#teamSelect').val();
  order_by = $('#orderbySelect').val();
  display_count = $('#displaycountSelect').val();
  $.getJSON('/api/stats/batting/' + year + '/' + team + '/' + order_by + '/' + display_count + '/', function(data){
    if (data.error){
      alert('There was an issue getting the matches!')
    }else{
      $('#stats-table tbody').empty()
      data = data.data;
      if (data.stats.length != 0){
        $('#stats-error-message').css('display', 'none');
        $.each(data.stats, function(i, item){
          var $tr = $('<tr>').append(
            $('<td>').html(item.player_name),
            $('<td>').html(item.games),
            $('<td>').html(item.innings),
            $('<td>').html(item.not_outs),
            $('<td>').html(item.runs),
            $('<td>').html(item.par_runs),
            $('<td>').html(item.high_score),
            $('<td>').html(item.average),
            $('<td>').html(item.runs_50s),
            $('<td>').html(item.runs_100s),
          ).appendTo('#stats-table tbody');
        });
      }else{
        $('#stats-error-message').css('display', 'block')
      };
    };
  });
};

function bowlingStatsSearch(){
  year = $('#yearSelect').val();
  team = $('#teamSelect').val();
  order_by = $('#orderbySelect').val();
  display_count = $('#displaycountSelect').val();
  $.getJSON('/api/stats/bowling/' + year + '/' + team + '/' + order_by + '/' + display_count + '/', function(data){
    if (data.error){
      alert('There was an issue getting the matches!')
    }else{
      $('#stats-table tbody').empty();
      data = data.data;
      if (data.stats.length != 0){
        $('#stats-error-message').css('display', 'none');
        $.each(data.stats, function(i, item){
          var $tr = $('<tr>').append(
            $('<td>').html(item.player_name),
            $('<td>').html(item.overs),
            $('<td>').html(item.maidens),
            $('<td>').html(item.runs),
            $('<td>').html(item.wickets),
            $('<td>').html(item.average),
            $('<td>').html(item.economy),
            $('<td>').html(item.wickets_5),
          ).appendTo('#stats-table tbody');
        });
      }else{
        $('#stats-error-message').css('display', 'block')
      };
    };
  });
};


function fieldingStatsSearch(){
  year = $('#yearSelect').val();
  team = $('#teamSelect').val();
  order_by = $('#orderbySelect').val();
  display_count = $('#displaycountSelect').val();
  $.getJSON('/api/stats/fielding/' + year + '/' + team + '/' + order_by + '/' + display_count + '/', function(data){
    if (data.error){
      alert('There was an issue getting the matches!')
    }else{
      $('#stats-table tbody').empty()
      data = data.data;
      if (data.stats.length != 0){
        $('#stats-error-message').css('display', 'none');
        $.each(data.stats, function(i, item){
          var $tr = $('<tr>').append(
            $('<td>').html(item.player_name),
            $('<td>').html(item.games),
            $('<td>').html(item.wk_catches),
            $('<td>').html(item.wk_stumpings),
            $('<td>').html(item.wk_total),
            $('<td>').html(item.fld_catches),
            $('<td>').html(item.fld_run_outs),
            $('<td>').html(item.fld_total),
          ).appendTo('#stats-table tbody');
        });
      }else{
        $('#stats-error-message').css('display', 'block')
      };
    };
  });
};
