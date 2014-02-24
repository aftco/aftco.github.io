var TagManager = function(){
  this.JSON_TAGS_URL = "/tags_json/";
  this._tags = null;

  var self = this;
  $.ajax({
    url: this.JSON_TAGS_URL,
    dataType: "json",
    success: function (data) {
      self._tags = {};
      for (var p in data) {
        if (data.hasOwnProperty(p)) {
          var lp = p.toLowerCase();
          self._tags[lp] = data[p];
        }
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
    }
  });
};

TagManager.prototype = {
  getTagPosts: function(tag) {
    var lt = tag.toLowerCase();
    if (!this._tags.hasOwnProperty(lt)) {
      return null;
    }
    return this._tags[lt];
  },
  _doIndex: function() { },
  activateExpiration: function(id) { }
};
