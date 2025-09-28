FROM jekyll/jekyll

COPY Gemfile .
COPY Gemfile.lock .

# RUN bundle install --quiet --clean
RUN bundle install --quiet && bundle clean --force

CMD ["jekyll", "serve"]
