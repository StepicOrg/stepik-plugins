require(["app/app"], function(app) {
  app.App.ApplicationRoute = Ember.Route.extend({
    model: function() {
      App.QuizPluginComponent.pluginRegistry['matching'] = {is_component: false};
      return App.QuizPluginComponent.loadPlugin(QUIZ_NAME).then(function(config) {
        window.model  = Ember.Object.create({
          config: config,
          display: {
            dataset: null,
            dataset_url: null,
            reply: null,
            previous_reply: null,
            is_reply_ready: true,
            content: null,
            disabled: false
          },
          editor: {
            source: null
          },
          log: [],
          has_dataset: false
        });
        return window.model;
      });
    }
  });

  App.ApplicationController = Ember.Controller.extend({

    log: function(msg) {
      console.log(msg);
      var new_log = [msg].concat(this.get('model.log'));
      this.set('model.log', new_log);
    },

    doAjax: function(url, data) {
      var log = this.log.bind(this);
      start = "POST to " + url + "\n";
      return Ember.$.ajax(url, {
        'type': 'post',
        'data': JSON.stringify(data),
        'contentType': 'application/json'
      }).done(function(data) {
        log(start + JSON.stringify(data));
        return data;
      }).fail(function(data) {
        log(start + "Failed\n" + data.responseText);
        return data;
      });
    },

    actions: {
      disable: function() {
        toggleProperty('model.disabled');
      },
      attempt: function() {
        var that=this;
        this.doAjax('quiz/attempt/').then(function(data){
          that.set('model.display.reply', null);
          that.set('model.display.dataset', data);
          that.set('model.has_dataset', true);
        });
      }
    }
  });

  App.ApplicationView = Ember.View.extend({
    actions: {
      submit: function() {
        var reply = this.get('pluginInstance').getReply();
        this.get('controller').doAjax('quiz/submission/', reply).then(function(data){
          window.model.set('display.dataset', window.model.get('display.dataset'));
          window.model.set('display.reply', {ordering: reply.ordering});
        });
      },
      updateSource: function() {
        this.get('controller').doAjax(
          'quiz/', this.get('quizEditorInstance').getSource());
      }
    }
  });

  app.App.QuizPluginComponent.reopenClass({
    getStaticPrefix: function (name) {
      return "/quiz/static/"
    }
  });

  app.App.advanceReadiness();
})
